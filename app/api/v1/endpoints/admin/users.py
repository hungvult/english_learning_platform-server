"""Admin endpoints: user management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
import uuid

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.schemas.admin import AdminUserRead, AdminUserUpdate

router = APIRouter()


def _to_admin_user_read(user: User) -> AdminUserRead:
    return AdminUserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=bool(user.is_admin),
        cefr_level=user.cefr_level,
        total_xp=user.total_xp or 0,
        hearts=user.hearts or 0,
        gems=user.gems or 0,
        current_streak=user.current_streak or 0,
        last_activity_at=user.last_activity_at,
        created_at=user.created_at,
    )


@router.get("/", response_model=List[AdminUserRead], summary="List all users")
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Return a paginated list of every registered user."""
    rows = db.exec(select(User).order_by(User.id).offset(skip).limit(limit)).all()
    return [_to_admin_user_read(row) for row in rows]


@router.get("/{user_id}", response_model=AdminUserRead, summary="Get user by ID")
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _to_admin_user_read(user)


@router.patch("/{user_id}", response_model=AdminUserRead, summary="Update user")
def update_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Update allowed user profile fields (admin role changes are disabled)."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = payload.model_dump(exclude_unset=True)
    # Defense in depth: never allow role elevation via this endpoint.
    update_data.pop("is_admin", None)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_admin_user_read(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
