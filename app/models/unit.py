from typing import List
from sqlmodel import SQLModel, Field, Relationship
import uuid


class Unit(SQLModel, table=True):
    __tablename__ = "Units"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    course_id: uuid.UUID = Field(foreign_key="Courses.id")
    title: str
    order_index: int

    course: "Course" = Relationship(back_populates="units")
    lessons: List["Lesson"] = Relationship(back_populates="unit")
