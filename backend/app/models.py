import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submissions: Mapped[list["Submission"]] = relationship(back_populates="user")


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    title: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String, default="easy")  # easy|medium|hard
    # Test cases stored as JSON: [{"input": "...", "expected": "...", "is_hidden": false}]
    test_cases: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Starter code template
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    # Solution for hint generation context (never sent to frontend)
    solution_hint: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submissions: Mapped[list["Submission"]] = relationship(back_populates="problem")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    problem_id: Mapped[str] = mapped_column(ForeignKey("problems.id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    # Result: pending | running | passed | failed | error | timeout
    status: Mapped[str] = mapped_column(String, default="pending")
    # Per-test results stored as JSON
    test_results: Mapped[dict] = mapped_column(JSON, nullable=True)
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="submissions")
    problem: Mapped["Problem"] = relationship(back_populates="submissions")
    hints: Mapped[list["Hint"]] = relationship(back_populates="submission")


class Hint(Base):
    __tablename__ = "hints"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    submission_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1=vague 2=specific 3=near-solution
    content: Mapped[str] = mapped_column(Text, nullable=False)
    was_helpful: Mapped[bool] = mapped_column(Boolean, nullable=True)  # user feedback
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    submission: Mapped["Submission"] = relationship(back_populates="hints")
