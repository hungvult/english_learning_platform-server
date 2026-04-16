from typing import List, Optional, Set

from sqlmodel import Session, select

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.unit import Unit
from app.models.user import User
from app.models.user_lesson_progress import UserLessonProgress
from app.schemas.client_progress import (
    ActiveLessonCompat,
    CourseCompact,
    CourseProgressResponse,
    LessonSummaryCompat,
    UnitSummaryCompat,
    UserProgressResponse,
)


class ClientProgressService:
    @staticmethod
    def _resolve_active_course(db: Session, user: User) -> Optional[Course]:
        courses = db.exec(select(Course)).all()
        if not courses:
            return None

        if user.cefr_level:
            matched = next(
                (course for course in courses if course.expected_cefr_level == user.cefr_level),
                None,
            )
            if matched:
                return matched

        return sorted(courses, key=lambda course: course.title)[0]

    @staticmethod
    def _completed_lesson_ids(db: Session, user_id) -> Set:
        rows = db.exec(
            select(UserLessonProgress.lesson_id).where(UserLessonProgress.user_id == user_id)
        ).all()
        return set(rows)

    @staticmethod
    def _build_units(
        db: Session, course_id, completed_lesson_ids: Set
    ) -> List[UnitSummaryCompat]:
        units = db.exec(
            select(Unit).where(Unit.course_id == course_id).order_by(Unit.order_index)
        ).all()

        unit_summaries: List[UnitSummaryCompat] = []
        for unit in units:
            lessons = db.exec(
                select(Lesson).where(Lesson.unit_id == unit.id).order_by(Lesson.order_index)
            ).all()

            lesson_summaries = [
                LessonSummaryCompat(
                    id=lesson.id,
                    title=lesson.title,
                    order=lesson.order_index,
                    completed=lesson.id in completed_lesson_ids,
                )
                for lesson in lessons
            ]

            unit_summaries.append(
                UnitSummaryCompat(
                    id=unit.id,
                    courseId=unit.course_id,
                    title=unit.title,
                    description="Practice and review lessons.",
                    order=unit.order_index,
                    lessons=lesson_summaries,
                )
            )

        return unit_summaries

    def get_user_progress(self, db: Session, user: User) -> UserProgressResponse:
        active_course = self._resolve_active_course(db, user)
        active_course_payload = (
            CourseCompact(
                id=active_course.id,
                title=active_course.title,
                imageSrc="/learn.svg",
            )
            if active_course
            else None
        )

        return UserProgressResponse(
            userId=user.id,
            activeCourse=active_course_payload,
            hearts=user.hearts,
            points=user.total_xp,
            streak=user.current_streak,
        )

    def get_active_course_units(self, db: Session, user: User) -> List[UnitSummaryCompat]:
        active_course = self._resolve_active_course(db, user)
        if not active_course:
            return []

        completed_lesson_ids = self._completed_lesson_ids(db, user.id)
        return self._build_units(db, active_course.id, completed_lesson_ids)

    def get_course_progress(self, db: Session, user: User) -> CourseProgressResponse:
        active_course = self._resolve_active_course(db, user)
        if not active_course:
            return CourseProgressResponse(activeLesson=None, activeLessonPercentage=0)

        completed_lesson_ids = self._completed_lesson_ids(db, user.id)
        units = self._build_units(db, active_course.id, completed_lesson_ids)

        first_lesson: Optional[LessonSummaryCompat] = None
        first_lesson_unit: Optional[UnitSummaryCompat] = None
        active_lesson: Optional[LessonSummaryCompat] = None
        active_lesson_unit: Optional[UnitSummaryCompat] = None

        for unit in units:
            for lesson in unit.lessons:
                if first_lesson is None:
                    first_lesson = lesson
                    first_lesson_unit = unit

                if not lesson.completed and active_lesson is None:
                    active_lesson = lesson
                    active_lesson_unit = unit

        if active_lesson is None:
            active_lesson = first_lesson
            active_lesson_unit = first_lesson_unit

        if active_lesson is None or active_lesson_unit is None:
            return CourseProgressResponse(activeLesson=None, activeLessonPercentage=0)

        return CourseProgressResponse(
            activeLesson=ActiveLessonCompat(
                id=active_lesson.id,
                title=active_lesson.title,
                order=active_lesson.order,
                completed=active_lesson.completed,
                unit=active_lesson_unit,
            ),
            activeLessonPercentage=100 if active_lesson.completed else 0,
        )


client_progress_service = ClientProgressService()
