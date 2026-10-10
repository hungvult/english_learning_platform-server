"""
Admin-facing request/response schemas.
These are separate from user-facing schemas so write fields
(e.g., is_admin, order_index) are never accidentally exposed to regular users.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr

# ---------------------------------------------------------------------------
# User admin schemas
# ---------------------------------------------------------------------------


class AdminUserRead(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    is_admin: bool
    cefr_level: str | None = None
    total_xp: int | None = 0
    hearts: int | None = 0
    gems: int | None = 0
    current_streak: int | None = 0
    last_activity_at: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class AdminUserUpdate(BaseModel):
    """Fields an admin can change on any user account."""

    username: str | None = None
    email: EmailStr | None = None
    cefr_level: str | None = None
    hearts: int | None = None
    gems: int | None = None
    total_xp: int | None = None
    current_streak: int | None = None


# ---------------------------------------------------------------------------
# Course schemas
# ---------------------------------------------------------------------------


class CourseCreate(BaseModel):
    title: str
    expected_cefr_level: str  # A1, A2, B1, B2, C1, C2


class CourseUpdate(BaseModel):
    title: str | None = None
    expected_cefr_level: str | None = None


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
    title: str | None = None
    order_index: int | None = None


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
    unit_id: uuid.UUID | None = None
    lesson_form_id: uuid.UUID | None = None
    title: str | None = None
    order_index: int | None = None


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
    order_index: int = 0
    question_data: dict[str, Any] | None = None
    answer_data: dict[str, Any] = {}


class ExerciseUpdate(BaseModel):
    lesson_id: uuid.UUID | None = None
    exercise_type_id: uuid.UUID | None = None
    order_index: int | None = None
    question_data: dict[str, Any] | None = None
    answer_data: dict[str, Any] | None = None


class ExerciseReadAdmin(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    exercise_type_id: uuid.UUID
    order_index: int = 0
    question_data: dict[str, Any] | None = None
    answer_data: dict[str, Any]

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


class ExerciseDependencySummary(BaseModel):
    exercise_id: uuid.UUID
    lesson_id: uuid.UUID
    dependent_user_exercise_logs: int
