from datetime import datetime, timezone
import uuid
from sqlalchemy import UnicodeText
from sqlmodel import SQLModel, Field, Relationship

class UserExerciseLog(SQLModel, table=True):
    __tablename__ = "UserExerciseLog"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="Users.id")
    lesson_id: uuid.UUID = Field(foreign_key="Lessons.id")
    exercise_id: uuid.UUID = Field(foreign_key="Exercises.id")

    # Store exact answer payload submitted
    user_answer: str = Field(sa_type=UnicodeText)
    is_correct: bool

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    user: "User" = Relationship(back_populates="exercise_logs")
    lesson: "Lesson" = Relationship(back_populates="exercise_logs")
    exercise: "Exercise" = Relationship(back_populates="logs")
