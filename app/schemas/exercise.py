from typing import Dict, Any
from pydantic import BaseModel
import uuid


class ExerciseRead(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    exercise_type_id: uuid.UUID
    question_data: Dict[str, Any] = {}
    answer_data: Dict[str, Any] = {}

    class Config:
        from_attributes = True
