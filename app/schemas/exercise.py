from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel
import uuid


# ---------------------------------------------------------------------------
# Client-facing: exercise WITHOUT answer_data
# ---------------------------------------------------------------------------

class ExerciseClient(BaseModel):
    """Exercise payload sent to clients during a lesson session.
    AnswerData is intentionally omitted — evaluation is done client-side
    from the pre-fetched payload or server-side via /evaluate.
    """
    id: uuid.UUID
    lesson_id: uuid.UUID
    type: str                           # exercise type name
    question_data: Dict[str, Any] = {}

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


# ---------------------------------------------------------------------------
# Evaluate endpoint  (server-side correctness check)
# ---------------------------------------------------------------------------

class EvaluateRequest(BaseModel):
    exercise_id: uuid.UUID
    user_answer: Any                    # raw answer — shape varies per type


class EvaluateResponse(BaseModel):
    is_correct: bool
    answer_data: Dict[str, Any]         # Reveal correct answer after check
