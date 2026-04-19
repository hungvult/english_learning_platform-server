"""
Admin-facing request/response schemas.
These are separate from user-facing schemas so write fields
(e.g., is_admin, order_index) are never accidentally exposed to regular users.
"""
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
import uuid


# ---------------------------------------------------------------------------
# User admin schemas
# ---------------------------------------------------------------------------

class AdminUserRead(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_admin: bool
    cefr_level: Optional[str] = None
    total_xp: int
    hearts: int
    gems: int
    current_streak: int
    last_activity_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    """Fields an admin can change on any user account."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = None
    cefr_level: Optional[str] = None
    hearts: Optional[int] = None
    gems: Optional[int] = None
    total_xp: Optional[int] = None


# ---------------------------------------------------------------------------
# Course schemas
# ---------------------------------------------------------------------------

class CourseCreate(BaseModel):
    title: str
    expected_cefr_level: str  # A1, A2, B1, B2, C1, C2


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    expected_cefr_level: Optional[str] = None


class CourseReadAdmin(BaseModel):
    id: uuid.UUID
    title: str
    expected_cefr_level: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Unit schemas
# ---------------------------------------------------------------------------

class UnitCreate(BaseModel):
    course_id: uuid.UUID
    title: str
    order_index: int


class UnitUpdate(BaseModel):
    title: Optional[str] = None
    order_index: Optional[int] = None


class UnitReadAdmin(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    order_index: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Lesson schemas
# ---------------------------------------------------------------------------

class LessonCreate(BaseModel):
    unit_id: uuid.UUID
    lesson_form_id: uuid.UUID
    title: str
    order_index: int


class LessonUpdate(BaseModel):
    unit_id: Optional[uuid.UUID] = None
    lesson_form_id: Optional[uuid.UUID] = None
    title: Optional[str] = None
    order_index: Optional[int] = None


class LessonReadAdmin(BaseModel):
    id: uuid.UUID
    unit_id: uuid.UUID
    lesson_form_id: uuid.UUID
    title: str
    order_index: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Exercise schemas
# ---------------------------------------------------------------------------

class ExerciseCreate(BaseModel):
    lesson_id: uuid.UUID
    exercise_type_id: uuid.UUID
    question_data: Optional[Dict[str, Any]] = None
    answer_data: Dict[str, Any] = {}


class ExerciseUpdate(BaseModel):
    lesson_id: Optional[uuid.UUID] = None
    exercise_type_id: Optional[uuid.UUID] = None
    question_data: Optional[Dict[str, Any]] = None
    answer_data: Optional[Dict[str, Any]] = None


class ExerciseReadAdmin(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    exercise_type_id: uuid.UUID
    question_data: Optional[Dict[str, Any]] = None
    answer_data: Dict[str, Any]

    class Config:
        from_attributes = True


class ExerciseTypeReadAdmin(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True


class MistakeAnalytics(BaseModel):
    user_answer: str
    count: int
