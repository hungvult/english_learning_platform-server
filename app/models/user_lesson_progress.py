import uuid
from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel


class UserLessonProgress(SQLModel, table=True):
    __tablename__ = "UserLessonProgress"

    user_id: uuid.UUID = Field(foreign_key="Users.id", primary_key=True)
    lesson_id: uuid.UUID = Field(foreign_key="Lessons.id", primary_key=True)
    score: int
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    user: "User" = Relationship(back_populates="lesson_progress")
    lesson: "Lesson" = Relationship(back_populates="lesson_progress")
