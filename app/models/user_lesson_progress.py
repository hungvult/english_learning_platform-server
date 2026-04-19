from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
import uuid


class UserLessonProgress(SQLModel, table=True):
    __tablename__ = "UserLessonProgress"

    user_id: uuid.UUID = Field(foreign_key="Users.id", primary_key=True)
    lesson_id: uuid.UUID = Field(foreign_key="Lessons.id", primary_key=True)
    score: int
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="lesson_progress")
    lesson: "Lesson" = Relationship(back_populates="lesson_progress")
