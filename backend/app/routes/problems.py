from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Problem, User
from app.schemas import ProblemOut, ProblemListItem
from app.services.auth_utils import get_current_user

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/", response_model=list[ProblemListItem])
async def list_problems(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Problem).order_by(Problem.difficulty, Problem.title))
    problems = result.scalars().all()
    return problems


@router.get("/{slug}", response_model=ProblemOut)
async def get_problem(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Problem).where(Problem.slug == slug))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")

    # Filter out hidden test cases before sending to frontend
    public_test_cases = [
        tc for tc in problem.test_cases if not tc.get("is_hidden", False)
    ]

    return ProblemOut(
        id=problem.id,
        title=problem.title,
        slug=problem.slug,
        description=problem.description,
        difficulty=problem.difficulty,
        test_cases=public_test_cases,
        starter_code=problem.starter_code,
    )
