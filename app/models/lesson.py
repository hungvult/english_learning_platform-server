import uuid

from sqlalchemy import Unicode
from sqlmodel import Field, Relationship, SQLModel


class LessonForm(SQLModel, table=True):
    __tablename__ = "LessonForms"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(sa_type=Unicode(100))  # 'new knowledge', 'review', 'test'

    lessons: list["Lesson"] = Relationship(back_populates="lesson_form")


class Lesson(SQLModel, table=True):
    __tablename__ = "Lessons"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    unit_id: uuid.UUID = Field(foreign_key="Units.id")
    lesson_form_id: uuid.UUID = Field(foreign_key="LessonForms.id")
    title: str = Field(sa_type=Unicode(255))
    order_index: int

    unit: "Unit" = Relationship(back_populates="lessons")
    lesson_form: LessonForm = Relationship(back_populates="lessons")
    exercises: list["Exercise"] = Relationship(back_populates="lesson")
    lesson_progress: list["UserLessonProgress"] = Relationship(back_populates="lesson")
    exercise_logs: list["UserExerciseLog"] = Relationship(back_populates="lesson")
