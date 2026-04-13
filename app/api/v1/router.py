from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, courses, lessons, exercises

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
