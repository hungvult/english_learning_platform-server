import uuid

from pydantic import BaseModel


class CourseRead(BaseModel):
    id: uuid.UUID
    title: str
    expected_cefr_level: str

    class Config:
        from_attributes = True


class UnitRead(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    order_index: int

    class Config:
        from_attributes = True


class LessonBrief(BaseModel):
    """Lesson summary within a unit listing (no exercises)."""

    id: uuid.UUID
    unit_id: uuid.UUID
    lesson_form_id: uuid.UUID
    title: str
    order_index: int

    class Config:
        from_attributes = True


class UnitWithLessons(UnitRead):
    lessons: list[LessonBrief] = []


class CourseWithUnits(CourseRead):
    units: list[UnitWithLessons] = []


class CourseClientResponse(BaseModel):
    id: str
    title: str
    imageSrc: str


class UserCoursesResponse(BaseModel):
    activeCourseId: str | None = None
    courses: list[CourseClientResponse]
