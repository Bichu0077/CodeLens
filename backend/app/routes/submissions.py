"""
submissions.py — The heart of CodeLens.

POST /submissions/          — creates a submission record
WS  /submissions/ws/{id}   — streams test results in real time
POST /submissions/{id}/hint — generates a grounded LLM hint
PUT  /submissions/{id}/hint/{hint_id}/feedback — records user feedback
"""

import json
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db, AsyncSessionLocal
from app.models import Submission, Problem, User, Hint
from app.schemas import SubmissionCreate, SubmissionOut, HintRequest, HintOut, HintFeedback
from app.services.auth_utils import get_current_user
from app.services.executor import run_tests_streamed
from app.services.hint import generate_hint

router = APIRouter(prefix="/submissions", tags=["submissions"])


# ── Create submission ─────────────────────────────────────────────────────────

@router.post("/", response_model=SubmissionOut, status_code=201)
async def create_submission(
    body: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify problem exists
    result = await db.execute(select(Problem).where(Problem.id == body.problem_id))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    submission = Submission(
        user_id=current_user.id,
        problem_id=body.problem_id,
        code=body.code,
        status="pending",
        total_count=len(problem.test_cases),
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


# ── WebSocket — stream test results ──────────────────────────────────────────

@router.websocket("/ws/{submission_id}")
async def stream_results(
    websocket: WebSocket,
    submission_id: str,
):
    await websocket.accept()

    async with AsyncSessionLocal() as db:
        # Load submission with problem
        result = await db.execute(
            select(Submission)
            .where(Submission.id == submission_id)
            .options(selectinload(Submission.problem))
        )
        submission = result.scalar_one_or_none()

        if not submission:
            await websocket.send_json({"error": "Submission not found"})
            await websocket.close()
            return

        problem = submission.problem

        # Update status to running
        submission.status = "running"
        await db.commit()

        # Notify client we're starting
        await websocket.send_json({"type": "start", "total": len(problem.test_cases)})

        all_results = []
        passed = 0

        try:
            async for test_result in run_tests_streamed(
                code=submission.code,
                test_cases=problem.test_cases,
            ):
                # Mark hidden tests
                idx = test_result.get("index", 0)
                if idx < len(problem.test_cases):
                    test_result["is_hidden"] = problem.test_cases[idx].get("is_hidden", False)
                    if test_result["is_hidden"]:
                        # Don't reveal hidden test case inputs/expected
                        test_result["input"] = "hidden"
                        test_result["expected"] = "hidden"

                if test_result.get("status") == "passed":
                    passed += 1

                all_results.append(test_result)

                # Stream each result immediately
                await websocket.send_json({"type": "result", "data": test_result})

        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"[submissions.ws] execution error: {type(e).__name__}: {e}")
            await websocket.send_json({"type": "error", "message": str(e)})

        # Determine final status
        final_status = "passed" if passed == len(problem.test_cases) else "failed"

        # Persist final results
        submission.status = final_status
        submission.test_results = all_results
        submission.passed_count = passed
        await db.commit()

        # Send completion message
        await websocket.send_json({
            "type": "complete",
            "status": final_status,
            "passed": passed,
            "total": len(problem.test_cases),
        })

        await websocket.close()


# ── Hints ─────────────────────────────────────────────────────────────────────

@router.post("/{submission_id}/hint", response_model=HintOut)
async def request_hint(
    submission_id: str,
    body: HintRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Load submission with all relations
    result = await db.execute(
        select(Submission)
        .where(Submission.id == submission_id, Submission.user_id == current_user.id)
        .options(selectinload(Submission.problem), selectinload(Submission.hints))
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if not submission.test_results:
        raise HTTPException(status_code=400, detail="Run your code first before requesting a hint.")

    # Find the first failing test to ground the hint
    failing_test = next(
        (t for t in submission.test_results if t.get("status") != "passed"),
        None,
    )
    if not failing_test:
        raise HTTPException(status_code=400, detail="All tests are passing — no hint needed!")

    # Collect prior hints so LLM doesn't repeat them
    prior_hint_texts = [h.content for h in sorted(submission.hints, key=lambda h: h.created_at)]

    hint_text = await generate_hint(
        problem_title=submission.problem.title,
        problem_description=submission.problem.description,
        user_code=submission.code,
        failing_test=failing_test,
        passed_count=submission.passed_count,
        total_count=submission.total_count,
        hint_level=body.level,
        prior_hints=prior_hint_texts,
    )

    hint = Hint(
        submission_id=submission_id,
        level=body.level,
        content=hint_text,
    )
    db.add(hint)
    await db.commit()
    await db.refresh(hint)
    return hint


@router.put("/{submission_id}/hint/{hint_id}/feedback")
async def hint_feedback(
    submission_id: str,
    hint_id: str,
    body: HintFeedback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Hint).where(Hint.id == hint_id))
    hint = result.scalar_one_or_none()
    if not hint:
        raise HTTPException(status_code=404, detail="Hint not found.")
    hint.was_helpful = body.was_helpful
    await db.commit()
    return {"ok": True}


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/me", response_model=list[SubmissionOut])
async def my_submissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Submission)
        .where(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()
