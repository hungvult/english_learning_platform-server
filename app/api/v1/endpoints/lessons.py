from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.lesson import LessonPayload
from app.schemas.progress import LessonSubmission, ProgressResponse
from app.services.lesson import lesson_service

router = APIRouter()


@router.get("/{lesson_id}/payload", response_model=LessonPayload)
def get_lesson_payload(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Pre-fetch the full lesson payload (all exercises with questions and answers)
    for client-side caching and offline evaluation.
    """
    lesson = lesson_service.get_lesson_payload(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    return lesson


@router.post("/{lesson_id}/submit", response_model=ProgressResponse)
def submit_lesson(
    lesson_id: uuid.UUID,
    submission: LessonSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit the final lesson completion payload.
    Server calculates XP, updates streak/hearts, and records progress.
    """
    return lesson_service.submit_lesson(db, current_user, lesson_id, submission)
