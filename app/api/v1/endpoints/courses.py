from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import uuid

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.client_progress import UnitSummaryCompat
from app.schemas.course import CourseRead, CourseWithUnits
from app.services.client_progress import client_progress_service
from app.services.course import course_service

router = APIRouter()


@router.get("/", response_model=List[CourseRead])
def list_courses(db: Session = Depends(get_db)):
    """List all available courses."""
    return course_service.list_courses(db)


@router.get("/active/units", response_model=List[UnitSummaryCompat])
def list_active_course_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compatibility endpoint for frontend learn page unit list."""
    return client_progress_service.get_active_course_units(db, current_user)


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
