import uuid

from pydantic import BaseModel


class CourseCompact(BaseModel):
    id: uuid.UUID
    title: str
    imageSrc: str


class UserProgressResponse(BaseModel):
    userId: uuid.UUID
    activeCourse: CourseCompact | None = None
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
    lessons: list[LessonSummaryCompat]


class ActiveLessonCompat(LessonSummaryCompat):
    unit: UnitSummaryCompat


class CourseProgressResponse(BaseModel):
    activeLesson: ActiveLessonCompat | None = None
    activeLessonPercentage: int
