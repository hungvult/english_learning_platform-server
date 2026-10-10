import uuid
from datetime import UTC, datetime

from sqlalchemy import String, Unicode
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "Users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, sa_type=Unicode(150))
    email: str = Field(unique=True, index=True, sa_type=Unicode(254))
    hashed_password: str = Field(sa_type=String(255))
    is_admin: bool = Field(default=False)
    active_course_id: uuid.UUID | None = Field(default=None, foreign_key="Courses.id")
    cefr_level: str | None = Field(default=None, max_length=2)
    total_xp: int = Field(default=0)
    hearts: int = Field(default=5)
    gems: int = Field(default=0)
    current_streak: int = Field(default=0)
    last_activity_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    lesson_progress: list["UserLessonProgress"] = Relationship(back_populates="user")
    exercise_logs: list["UserExerciseLog"] = Relationship(back_populates="user")
