from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.course import Course
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
    def _resolve_active_course(db: Session, user: User) -> Course | None:
        if not user.active_course_id:
            return None

        return db.get(Course, user.active_course_id)

    @staticmethod
    def _completed_lesson_ids(db: Session, user_id) -> set:
        rows = db.exec(
            select(UserLessonProgress.lesson_id).where(UserLessonProgress.user_id == user_id)
        ).all()
        return set(rows)

    @staticmethod
    def _build_units(db: Session, course_id, completed_lesson_ids: set) -> list[UnitSummaryCompat]:
        units = db.exec(
            select(Unit)
            .where(Unit.course_id == course_id)
            .options(selectinload(Unit.lessons))
            .order_by(Unit.order_index)
        ).all()

        unit_summaries: list[UnitSummaryCompat] = []
        for unit in units:
            lessons = sorted(unit.lessons, key=lambda item: item.order_index)

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

    def get_active_course_units(self, db: Session, user: User) -> list[UnitSummaryCompat]:
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

        first_lesson: LessonSummaryCompat | None = None
        first_lesson_unit: UnitSummaryCompat | None = None
        active_lesson: LessonSummaryCompat | None = None
        active_lesson_unit: UnitSummaryCompat | None = None

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
