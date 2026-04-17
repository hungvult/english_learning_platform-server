from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.lesson import Lesson
from app.models.exercise import Exercise
from app.models.unit import Unit
from app.models.course import Course
from app.schemas.exercise import ExerciseClient, EvaluateRequest, EvaluateResponse
from app.schemas.lesson import LessonPayload
from app.schemas.progress import LessonSubmission, ProgressResponse
from app.services.lesson import lesson_service

router = APIRouter()


def _get_active_lesson(db: Session, user: User) -> Lesson:
    """Helper to resolve the user's active lesson."""
    if not user.active_course_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active course selected.",
        )
    # Find the first uncompleted lesson in the active course
    from app.models.user_lesson_progress import UserLessonProgress
    completed = db.exec(
        select(UserLessonProgress.lesson_id).where(UserLessonProgress.user_id == user.id)
    ).all()
    completed_ids = set(completed)

    units = db.exec(
        select(Unit)
        .where(Unit.course_id == user.active_course_id)
        .order_by(Unit.order_index)
    ).all()

    for unit in units:
        lessons = db.exec(
            select(Lesson)
            .where(Lesson.unit_id == unit.id)
            .order_by(Lesson.order_index)
        ).all()
        for lesson in lessons:
            if lesson.id not in completed_ids:
                return lesson

    # All completed — return the last lesson for practice
    if units:
        last_unit = units[-1]
        last_lesson = db.exec(
            select(Lesson)
            .where(Lesson.unit_id == last_unit.id)
            .order_by(Lesson.order_index.desc())
        ).first()
        if last_lesson:
            return last_lesson

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No lessons found for active course.",
    )


@router.get("/active/payload", response_model=LessonPayload)
def get_active_lesson_payload(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the pre-fetch payload for the user's current active lesson.
    Used by the /lesson shortcut page.
    """
    lesson = _get_active_lesson(db, current_user)
    # Eager-load exercises + their type
    lesson = db.exec(
        select(Lesson)
        .where(Lesson.id == lesson.id)
        .options(selectinload(Lesson.exercises).selectinload(Exercise.exercise_type))
    ).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found.")
    return lesson_service.build_client_payload(lesson)


@router.get("/{lesson_id}/payload", response_model=LessonPayload)
def get_lesson_payload(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Pre-fetch the full lesson payload (exercises with question_data) for
    client-side caching per Hybrid Validation Architecture (Spec §6.1).
    AnswerData is NOT included — the client evaluates deterministic exercises
    locally and sends the final result in a single submit call.
    """
    lesson = lesson_service.get_lesson_payload(db, lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    return lesson_service.build_client_payload(lesson)


@router.get("/{lesson_id}/exercises", response_model=List[ExerciseClient])
def get_lesson_exercises(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve exercises for a lesson without answer_data.
    Use for on-demand fetching when the full payload is not cached.
    """
    return lesson_service.get_exercises_for_lesson(db, lesson_id)


@router.post("/exercises/evaluate", response_model=EvaluateResponse)
def evaluate_exercise(
    req: EvaluateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Server-side evaluation for a single exercise answer (Spec §6.2).
    Returns is_correct and the correct answer_data.
    """
    return lesson_service.evaluate_exercise(db, req)


@router.post("/{lesson_id}/submit", response_model=ProgressResponse)
def submit_lesson(
    lesson_id: uuid.UUID,
    submission: LessonSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit the final lesson completion payload (Spec §6.4).
    Single POST after all exercises are done. Server finalises XP and progress.
    """
    return lesson_service.submit_lesson(db, current_user, lesson_id, submission)
