from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import uuid

from app.core.database import get_db
from app.schemas.course import CourseRead, CourseWithUnits
from app.services.course import course_service

router = APIRouter()


@router.get("/", response_model=List[CourseRead])
def list_courses(db: Session = Depends(get_db)):
    """List all available courses."""
    return course_service.list_courses(db)


@router.get("/{course_id}", response_model=CourseWithUnits)
def get_course(course_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a course with its full unit → lesson tree."""
    course = course_service.get_course_tree(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return course
