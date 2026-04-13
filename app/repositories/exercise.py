from typing import List
from sqlmodel import Session, select
import uuid

from app.models.exercise import Exercise
from app.repositories.base import BaseRepository


class ExerciseRepository(BaseRepository[Exercise]):
    def __init__(self):
        super().__init__(Exercise)

    def get_by_lesson(self, db: Session, lesson_id: uuid.UUID) -> List[Exercise]:
        statement = select(Exercise).where(Exercise.lesson_id == lesson_id)
        return db.exec(statement).all()


exercise_repository = ExerciseRepository()
