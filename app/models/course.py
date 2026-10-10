import uuid

from sqlalchemy import Unicode
from sqlmodel import Field, Relationship, SQLModel


class Course(SQLModel, table=True):
    __tablename__ = "Courses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(sa_type=Unicode(255))
    expected_cefr_level: str = Field(max_length=2)

    units: list["Unit"] = Relationship(back_populates="course")
