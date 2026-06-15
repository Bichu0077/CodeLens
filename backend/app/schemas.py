from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Problems ──────────────────────────────────────────────────────────────────

class TestCaseOut(BaseModel):
    input: str
    expected: str
    is_hidden: bool = False


class ProblemOut(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    difficulty: str
    # Only expose public test cases to the frontend
    test_cases: list[TestCaseOut]
    starter_code: str

    class Config:
        from_attributes = True


class ProblemListItem(BaseModel):
    id: str
    title: str
    slug: str
    difficulty: str

    class Config:
        from_attributes = True


# ── Submissions ───────────────────────────────────────────────────────────────

class SubmissionCreate(BaseModel):
    problem_id: str
    code: str


class TestResultOut(BaseModel):
    index: int
    status: str          # passed | failed | error | timeout
    input: str
    expected: str
    actual: Optional[str] = None
    error: Optional[str] = None
    elapsed_ms: Optional[float] = None
    is_hidden: bool = False


class SubmissionOut(BaseModel):
    id: str
    status: str
    test_results: Optional[list[TestResultOut]] = None
    passed_count: int
    total_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Hints ─────────────────────────────────────────────────────────────────────

class HintRequest(BaseModel):
    submission_id: str
    level: int  # 1, 2, or 3


class HintOut(BaseModel):
    id: str
    level: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class HintFeedback(BaseModel):
    was_helpful: bool
