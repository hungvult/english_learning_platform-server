from typing import Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
import uuid

from app.models.course import Course
from app.models.unit import Unit
from app.models.lesson import Lesson
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self):
        super().__init__(Course)

    def get_with_units(self, db: Session, course_id: uuid.UUID) -> Optional[Course]:
        """Eager-load units and their lessons for the course tree."""
        statement = (
            select(Course)
            .where(Course.id == course_id)
            .options(
                selectinload(Course.units)
                .selectinload(Unit.lessons)
            )
        )
        return db.exec(statement).first()


course_repository = CourseRepository()
