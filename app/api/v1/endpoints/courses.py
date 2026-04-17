from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
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


class CourseClientResponse(BaseModel):
    id: str
    title: str
    imageSrc: str


class UserCoursesResponse(BaseModel):
    activeCourseId: Optional[str] = None
    courses: List[CourseClientResponse]


@router.get("/me", response_model=UserCoursesResponse)
def get_user_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve courses alongside current user's active course ID."""
    courses = course_service.list_courses(db)

    client_courses = []
    for c in courses:
        client_courses.append({
            "id": str(c.id),
            "title": c.title,
            "imageSrc": "/us_flag.webp",
        })

    return {
        "activeCourseId": str(current_user.active_course_id) if current_user.active_course_id else None,
        "courses": client_courses
    }


@router.patch("/select")
def select_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Select the active course for the current user."""
    course = course_service.get_course_tree(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    current_user.active_course_id = course_id
    db.add(current_user)
    db.commit()
    return {"status": "success"}



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
