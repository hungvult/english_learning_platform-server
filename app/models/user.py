from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship, AutoString
from sqlalchemy import String
import uuid


class User(SQLModel, table=True):
    __tablename__ = "Users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, sa_type=String(150))
    email: str = Field(unique=True, index=True, sa_type=String(254))
    hashed_password: str
    is_admin: bool = Field(default=False)
    active_course_id: Optional[uuid.UUID] = Field(default=None, foreign_key="Courses.id")
    cefr_level: Optional[str] = Field(default=None, max_length=2)
    total_xp: int = Field(default=0)
    hearts: int = Field(default=5)
    gems: int = Field(default=0)
    current_streak: int = Field(default=0)
    last_activity_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    lesson_progress: List["UserLessonProgress"] = Relationship(back_populates="user")
