from fastapi import APIRouter

from app.api.v1.endpoints import auth, courses, lessons, users
from app.api.v1.endpoints.admin import (
    courses as admin_courses,
)
from app.api.v1.endpoints.admin import (
    exercise_types as admin_exercise_types,
)
from app.api.v1.endpoints.admin import (
    exercises as admin_exercises,
)
from app.api.v1.endpoints.admin import (
    lessons as admin_lessons,
)
from app.api.v1.endpoints.admin import (
    units as admin_units,
)
from app.api.v1.endpoints.admin import (
    users as admin_users,
)

api_router = APIRouter()

# ── Public / authenticated routes ──────────────────────────────────────────
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])

# ── Admin-only routes ───────────────────────────────────────────────────────
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["Admin — Users"])
api_router.include_router(admin_courses.router, prefix="/admin/courses", tags=["Admin — Courses"])
api_router.include_router(admin_units.router, prefix="/admin/units", tags=["Admin — Units"])
api_router.include_router(admin_lessons.router, prefix="/admin/lessons", tags=["Admin — Lessons"])
api_router.include_router(
    admin_exercises.router, prefix="/admin/exercises", tags=["Admin — Exercises"]
)
api_router.include_router(
    admin_exercise_types.router, prefix="/admin/exercise-types", tags=["Admin — Exercises"]
)
