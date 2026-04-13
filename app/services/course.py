from typing import List, Optional
from sqlmodel import Session
import uuid

from app.models.course import Course
from app.repositories.course import course_repository


class CourseService:
    def __init__(self):
        self.repository = course_repository

    def list_courses(self, db: Session) -> List[Course]:
        return self.repository.get_multi(db)

    def get_course_tree(self, db: Session, course_id: uuid.UUID) -> Optional[Course]:
        """Returns course with nested units → lessons."""
        return self.repository.get_with_units(db, course_id)


course_service = CourseService()
