from typing import Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.mssql import NVARCHAR
import uuid


class Exercise(SQLModel, table=True):
    __tablename__ = "Exercises"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lesson_id: uuid.UUID = Field(foreign_key="Lessons.id")
    type: str  # 'word_bank', 'listening', 'speaking', 'translation', 'matching'

    question_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(NVARCHAR(None)),
    )
    answer_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(NVARCHAR(None)),
    )

    lesson: "Lesson" = Relationship(back_populates="exercises")
