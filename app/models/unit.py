import uuid

from sqlalchemy import Unicode
from sqlmodel import Field, Relationship, SQLModel


class Unit(SQLModel, table=True):
    __tablename__ = "Units"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    course_id: uuid.UUID = Field(foreign_key="Courses.id")
    title: str = Field(sa_type=Unicode(255))
    order_index: int

    course: "Course" = Relationship(back_populates="units")
    lessons: list["Lesson"] = Relationship(back_populates="unit")
