from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel
import uuid


# ---------------------------------------------------------------------------
# Client-facing: exercise WITH answer_data for local evaluation
# ---------------------------------------------------------------------------

class ExerciseClient(BaseModel):
    """Exercise payload sent to clients during a lesson session.
    AnswerData IS included as the client evaluates exercises locally.
    """
    id: uuid.UUID
    lesson_id: uuid.UUID
    type: str                           # exercise type name
    question_data: Dict[str, Any] = {}
    answer_data: Dict[str, Any] = {}

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Full read (admin / pre-fetch includes answer_data)
# ---------------------------------------------------------------------------

class ExerciseRead(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    exercise_type_id: uuid.UUID
    type: str                           # resolved from exercise_type.name
    question_data: Dict[str, Any] = {}
    answer_data: Dict[str, Any] = {}

    class Config:
        from_attributes = True
