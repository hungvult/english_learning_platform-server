"""Admin endpoints: lesson management."""
from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import Session, select
import uuid

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.models.lesson import Lesson
from app.schemas.admin import LessonCreate, LessonUpdate, LessonReadAdmin

router = APIRouter()


@router.get("/", response_model=List[LessonReadAdmin], summary="List lessons")
def list_lessons(
    unit_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """List all lessons, optionally filtered by unit_id."""
    stmt = select(Lesson).order_by(Lesson.id)
    if unit_id:
        stmt = stmt.where(Lesson.unit_id == unit_id)
    return db.exec(stmt.offset(skip).limit(limit)).all()


@router.post("/", response_model=LessonReadAdmin, status_code=status.HTTP_201_CREATED, summary="Create lesson")
def create_lesson(
    payload: LessonCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    lesson = Lesson(**payload.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.get("/{lesson_id}", response_model=LessonReadAdmin, summary="Get lesson")
def get_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lesson


@router.patch("/{lesson_id}", response_model=LessonReadAdmin, summary="Update lesson")
def update_lesson(
    lesson_id: uuid.UUID,
    payload: LessonUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete lesson")
def delete_lesson(
    lesson_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    db.delete(lesson)
    db.commit()


@router.post("/swap-order", response_model=List[LessonReadAdmin], summary="Swap order_index between two lessons")
def swap_lesson_order(
    id_a: uuid.UUID = Body(...),
    id_b: uuid.UUID = Body(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Swap the order_index values of two lessons atomically."""
    lesson_a = db.get(Lesson, id_a)
    lesson_b = db.get(Lesson, id_b)
    if not lesson_a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson {id_a} not found")
    if not lesson_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson {id_b} not found")

    lesson_a.order_index, lesson_b.order_index = lesson_b.order_index, lesson_a.order_index
    db.add(lesson_a)
    db.add(lesson_b)
    db.commit()
    db.refresh(lesson_a)
    db.refresh(lesson_b)
    return [lesson_a, lesson_b]
