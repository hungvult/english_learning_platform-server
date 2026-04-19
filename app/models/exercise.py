import json
from typing import Any, Dict, List

from sqlalchemy import Column, String
from sqlalchemy.types import TypeDecorator
from sqlmodel import SQLModel, Field, Relationship
import uuid


class JSONString(TypeDecorator):
    """Store a Python dict as a JSON string in an NVARCHAR(MAX) column.
    Required for SQL Server which has no native JSON column type.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return value  # already serialised
        return json.dumps(value, ensure_ascii=False)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value == "":
            return {}
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return {}


class ExerciseType(SQLModel, table=True):
    __tablename__ = "ExerciseTypes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str  # e.g. COMPLETE_CONVERSATION, ARRANGE_WORDS …

    exercises: List["Exercise"] = Relationship(back_populates="exercise_type")


class Exercise(SQLModel, table=True):
    __tablename__ = "Exercises"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lesson_id: uuid.UUID = Field(foreign_key="Lessons.id")
    exercise_type_id: uuid.UUID = Field(foreign_key="ExerciseTypes.id")

    question_data: Dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSONString(length=None)),
    )
    answer_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONString(length=None)),
    )

    lesson: "Lesson" = Relationship(back_populates="exercises")
    exercise_type: ExerciseType = Relationship(back_populates="exercises")
    logs: List["UserExerciseLog"] = Relationship(back_populates="exercise")
