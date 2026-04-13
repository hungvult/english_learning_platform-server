from typing import Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
import uuid

from app.models.lesson import Lesson
from app.models.exercise import Exercise
from app.repositories.base import BaseRepository


class LessonRepository(BaseRepository[Lesson]):
    def __init__(self):
        super().__init__(Lesson)

    def get_with_exercises(self, db: Session, lesson_id: uuid.UUID) -> Optional[Lesson]:
        """Eager-load all exercises for the lesson payload pre-fetch."""
        statement = (
            select(Lesson)
            .where(Lesson.id == lesson_id)
            .options(selectinload(Lesson.exercises))
        )
        return db.exec(statement).first()


lesson_repository = LessonRepository()
