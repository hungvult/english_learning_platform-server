from typing import List
from pydantic import BaseModel
import uuid

from app.schemas.exercise import ExerciseClient


class LessonRead(BaseModel):
    id: uuid.UUID
    unit_id: uuid.UUID
    lesson_form_id: uuid.UUID
    title: str
    order_index: int

    class Config:
        from_attributes = True


class LessonPayload(LessonRead):
    """Full lesson payload with all exercises for client-side pre-fetch.
    AnswerData is included so the client can evaluate answers locally
    (Hybrid Client/Server Validation Architecture per Specification §6).
    """

    exercises: List[ExerciseClient] = []
