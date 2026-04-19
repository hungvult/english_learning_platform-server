"""Admin endpoints: exercise management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import json
import uuid

from sqlalchemy import func
from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.models.exercise import Exercise
from app.models.user_exercise_log import UserExerciseLog
from app.schemas.admin import ExerciseCreate, ExerciseUpdate, ExerciseReadAdmin, MistakeAnalytics

router = APIRouter()


def _serialize(exercise: Exercise) -> ExerciseReadAdmin:
    """Deserialize JSON string columns stored by SQLModel/MSSQL."""
    q = exercise.question_data
    a = exercise.answer_data
    if isinstance(q, str):
        q = json.loads(q)
    if isinstance(a, str):
        a = json.loads(a)
    return ExerciseReadAdmin(
        id=exercise.id,
        lesson_id=exercise.lesson_id,
        exercise_type_id=exercise.exercise_type_id,
        question_data=q,
        answer_data=a,
    )


@router.get("/", response_model=List[ExerciseReadAdmin], summary="List exercises")
def list_exercises(
    lesson_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """List all exercises, optionally filtered by lesson_id."""
    stmt = select(Exercise).order_by(Exercise.id)
    if lesson_id:
        stmt = stmt.where(Exercise.lesson_id == lesson_id)
    rows = db.exec(stmt.offset(skip).limit(limit)).all()
    return [_serialize(r) for r in rows]


from app.services.exercise_validation import validate_exercise_payload

@router.post("/", response_model=ExerciseReadAdmin, status_code=status.HTTP_201_CREATED, summary="Create exercise")
def create_exercise(
    payload: ExerciseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    safe_q, safe_a = validate_exercise_payload(
        db, payload.exercise_type_id, payload.question_data, payload.answer_data
    )

    data = payload.model_dump()
    # Store dicts as JSON strings (NVARCHAR column), respecting null constraints
    data["question_data"] = json.dumps(safe_q) if safe_q is not None else None
    data["answer_data"] = json.dumps(safe_a)

    exercise = Exercise(**data)
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return _serialize(exercise)


@router.get("/{exercise_id}", response_model=ExerciseReadAdmin, summary="Get exercise")
def get_exercise(
    exercise_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return _serialize(exercise)


@router.patch("/{exercise_id}", response_model=ExerciseReadAdmin, summary="Update exercise")
def update_exercise(
    exercise_id: uuid.UUID,
    payload: ExerciseUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    update_data = payload.model_dump(exclude_unset=True)

    if any(k in update_data for k in ["exercise_type_id", "question_data", "answer_data"]):
        target_type_id = update_data.get("exercise_type_id", exercise.exercise_type_id)

        # Need full merged data to perform cross-field validation
        q_data_raw = update_data.get("question_data", exercise.question_data)
        if isinstance(q_data_raw, str):
            q_data_raw = json.loads(q_data_raw)

        a_data_raw = update_data.get("answer_data", exercise.answer_data)
        if isinstance(a_data_raw, str):
            a_data_raw = json.loads(a_data_raw)

        safe_q, safe_a = validate_exercise_payload(db, target_type_id, q_data_raw, a_data_raw)

        if "question_data" in update_data:
            update_data["question_data"] = json.dumps(safe_q) if safe_q is not None else None
        if "answer_data" in update_data:
            update_data["answer_data"] = json.dumps(safe_a)

    # If there are manual updates to other fields or if the dumps are already set,
    # skip re-serializing because we handled it explicitly above.
    for key in ("question_data", "answer_data"):
        if key in update_data and isinstance(update_data[key], dict):
            update_data[key] = json.dumps(update_data[key])

    for field, value in update_data.items():
        setattr(exercise, field, value)
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return _serialize(exercise)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete exercise")
def delete_exercise(
    exercise_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    db.delete(exercise)
    db.commit()


@router.get("/{exercise_id}/logs", response_model=List[MistakeAnalytics], summary="Get common mistaken answers for exercise")
def get_exercise_logs(
    exercise_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Return the most common INCORRECT answers submitted for this exercise.
    Useful for admins to track user mistakes and improve question clarity.
    """
    stmt = (
        select(
            UserExerciseLog.user_answer,
            func.count(UserExerciseLog.id).label("count")
        )
        .where(UserExerciseLog.exercise_id == exercise_id)
        .where(UserExerciseLog.is_correct == False)
        .group_by(UserExerciseLog.user_answer)
        .order_by(func.count(UserExerciseLog.id).desc())
    )

    rows = db.exec(stmt).all()

    return [
        MistakeAnalytics(user_answer=row[0], count=row[1])
        for row in rows
    ]
