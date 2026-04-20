from typing import List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Unicode
import uuid


class Course(SQLModel, table=True):
    __tablename__ = "Courses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(sa_type=Unicode(255))
    expected_cefr_level: str = Field(max_length=2)

    units: List["Unit"] = Relationship(back_populates="course")
