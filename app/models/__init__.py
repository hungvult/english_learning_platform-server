# Re-export all models for convenient imports and Alembic discovery
from app.models.user import User
from app.models.course import Course
from app.models.unit import Unit
from app.models.lesson import LessonForm, Lesson
from app.models.exercise import Exercise
from app.models.user_lesson_progress import UserLessonProgress

__all__ = [
    "User",
    "Course",
    "Unit",
    "LessonForm",
    "Lesson",
    "Exercise",
    "UserLessonProgress",
]
