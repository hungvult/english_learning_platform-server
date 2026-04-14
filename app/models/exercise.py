from typing import Dict, Any, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.mssql import NVARCHAR
import uuid

class ExerciseType(SQLModel, table=True):
    __tablename__ = "ExerciseTypes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str  # 'word_bank', 'listening', 'speaking', 'translation', 'matching'

    exercises: List["Exercise"] = Relationship(back_populates="exercise_type")


class Exercise(SQLModel, table=True):
    __tablename__ = "Exercises"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lesson_id: uuid.UUID = Field(foreign_key="Lessons.id")
    exercise_type_id: uuid.UUID = Field(foreign_key="ExerciseTypes.id")

    question_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(NVARCHAR(None)),
    )
    answer_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(NVARCHAR(None)),
    )

    lesson: "Lesson" = Relationship(back_populates="exercises")
    exercise_type: ExerciseType = Relationship(back_populates="exercises")
