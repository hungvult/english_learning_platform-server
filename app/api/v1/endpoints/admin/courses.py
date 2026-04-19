"""Admin endpoints: course management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import uuid

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.models.course import Course
from app.schemas.admin import CourseCreate, CourseUpdate, CourseReadAdmin

router = APIRouter()


@router.get("/", response_model=List[CourseReadAdmin], summary="List all courses")
def list_courses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    from sqlmodel import select
    return db.exec(select(Course).order_by(Course.id).offset(skip).limit(limit)).all()


@router.post("/", response_model=CourseReadAdmin, status_code=status.HTTP_201_CREATED, summary="Create course")
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseReadAdmin, summary="Get course")
def get_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.patch("/{course_id}", response_model=CourseReadAdmin, summary="Update course")
def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete course")
def delete_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    db.delete(course)
    db.commit()
