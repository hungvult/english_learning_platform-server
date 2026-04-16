from typing import List, Optional
from pydantic import BaseModel
import uuid


class CourseCompact(BaseModel):
    id: uuid.UUID
    title: str
    imageSrc: str


class UserProgressResponse(BaseModel):
    userId: uuid.UUID
    activeCourse: Optional[CourseCompact] = None
    hearts: int
    points: int
    streak: int


class LessonSummaryCompat(BaseModel):
    id: uuid.UUID
    title: str
    order: int
    completed: bool


class UnitSummaryCompat(BaseModel):
    id: uuid.UUID
    courseId: uuid.UUID
    title: str
    description: str
    order: int
    lessons: List[LessonSummaryCompat]


class ActiveLessonCompat(LessonSummaryCompat):
    unit: UnitSummaryCompat


class CourseProgressResponse(BaseModel):
    activeLesson: Optional[ActiveLessonCompat] = None
    activeLessonPercentage: int
