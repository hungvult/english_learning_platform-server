import uuid

from sqlmodel import Session, select

from app.models.exercise import Exercise
from app.repositories.base import BaseRepository


class ExerciseRepository(BaseRepository[Exercise]):
    def __init__(self):
        super().__init__(Exercise)

    def get_by_lesson(self, db: Session, lesson_id: uuid.UUID) -> list[Exercise]:
        statement = select(Exercise).where(Exercise.lesson_id == lesson_id)
        return db.exec(statement).all()


exercise_repository = ExerciseRepository()
