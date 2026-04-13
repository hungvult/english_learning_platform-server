from typing import Optional
from datetime import datetime
from pydantic import BaseModel
import uuid


class UserRead(BaseModel):
    """Public user profile — never exposes hashed_password."""

    id: uuid.UUID
    username: str
    email: str
    cefr_level: Optional[str] = None
    total_xp: int
    hearts: int
    gems: int
    current_streak: int
    last_activity_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Fields a user can update on their own profile."""

    username: Optional[str] = None
    cefr_level: Optional[str] = None
