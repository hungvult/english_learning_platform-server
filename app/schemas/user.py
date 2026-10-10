import uuid
from datetime import datetime

from pydantic import BaseModel


class UserRead(BaseModel):
    """Public user profile — never exposes hashed_password."""

    id: uuid.UUID
    username: str
    email: str
    is_admin: bool
    active_course_id: uuid.UUID | None = None
    cefr_level: str | None = None
    total_xp: int
    hearts: int
    gems: int
    current_streak: int
    last_activity_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Fields a user can update on their own profile."""

    username: str | None = None
    email: str | None = None
    password: str | None = None
    active_course_id: uuid.UUID | None = None
    cefr_level: str | None = None
