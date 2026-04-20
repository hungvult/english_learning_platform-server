from typing import List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Unicode
import uuid


class LessonForm(SQLModel, table=True):
    __tablename__ = "LessonForms"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_type=Unicode(100))  # 'new knowledge', 'review', 'test'

    lessons: List["Lesson"] = Relationship(back_populates="lesson_form")


class Lesson(SQLModel, table=True):
    __tablename__ = "Lessons"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    unit_id: uuid.UUID = Field(foreign_key="Units.id")
    lesson_form_id: uuid.UUID = Field(foreign_key="LessonForms.id")
    title: str = Field(sa_type=Unicode(255))
    order_index: int

    unit: "Unit" = Relationship(back_populates="lessons")
    lesson_form: LessonForm = Relationship(back_populates="lessons")
    exercises: List["Exercise"] = Relationship(back_populates="lesson")
    lesson_progress: List["UserLessonProgress"] = Relationship(back_populates="lesson")
    exercise_logs: List["UserExerciseLog"] = Relationship(back_populates="lesson")
