from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid


class AnswerDetail(BaseModel):
    """Single exercise answer within the submission."""

    exercise_id: uuid.UUID
    user_answer: str
    is_correct: bool
    time_spent_ms: int = 0


class LessonSubmission(BaseModel):
    """
    The single final POST payload from the frontend after completing all
    exercises in a lesson (see Specification section 6.4).
    """

    answers: List[AnswerDetail]
    score: int
    hearts_left: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class ProgressResponse(BaseModel):
    """Server response after accepting a lesson submission."""

    xp_earned: int
    total_xp: int
    current_streak: int
    hearts: int
    gems: int
