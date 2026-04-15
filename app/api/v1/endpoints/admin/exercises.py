"""Admin endpoints: exercise management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import json
import uuid

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.models.exercise import Exercise
from app.schemas.admin import ExerciseCreate, ExerciseUpdate, ExerciseReadAdmin

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
    stmt = select(Exercise)
    if lesson_id:
        stmt = stmt.where(Exercise.lesson_id == lesson_id)
    rows = db.exec(stmt.offset(skip).limit(limit)).all()
    return [_serialize(r) for r in rows]


@router.post("/", response_model=ExerciseReadAdmin, status_code=status.HTTP_201_CREATED, summary="Create exercise")
def create_exercise(
    payload: ExerciseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    data = payload.model_dump()
    # Store dicts as JSON strings (NVARCHAR column)
    data["question_data"] = json.dumps(data["question_data"])
    data["answer_data"] = json.dumps(data["answer_data"])
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
    # Serialize dict fields before saving
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
