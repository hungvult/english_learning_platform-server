from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_db
from app.api.dependencies import require_authenticated_user
from app.models.user import User
from app.schemas.client_progress import (
    CourseProgressResponse,
    UserProgressResponse,
)
from app.schemas.user import UserRead, UserUpdate
from app.services.client_progress import client_progress_service
from app.services.user import user_service

router = APIRouter()


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(require_authenticated_user),
):
    """Get the currently authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserRead)
def update_current_user(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Update the currently authenticated user's profile."""
    return user_service.update_profile(db, current_user, payload)


@router.get("/me/progress", response_model=UserProgressResponse)
def read_current_user_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Compatibility endpoint for frontend user progress card data."""
    return client_progress_service.get_user_progress(db, current_user)


@router.get("/me/course-progress", response_model=CourseProgressResponse)
def read_current_user_course_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user),
):
    """Compatibility endpoint for frontend active lesson and progress state."""
    return client_progress_service.get_course_progress(db, current_user)
