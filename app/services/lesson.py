from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session
from fastapi import HTTPException, status
import uuid

from app.models.lesson import Lesson
from app.models.exercise import Exercise, ExerciseType
from app.models.user import User
from app.models.user_lesson_progress import UserLessonProgress
from app.schemas.exercise import ExerciseClient
from app.schemas.lesson import LessonPayload
from app.schemas.progress import LessonSubmission, ProgressResponse
from app.repositories.lesson import lesson_repository
from app.repositories.exercise import exercise_repository


# XP reward tiers based on accuracy percentage
XP_TIERS = [
    (1.0, 20),   # 100% accuracy → 20 XP
    (0.8, 15),   # 80%+ → 15 XP
    (0.5, 10),   # 50%+ → 10 XP
    (0.0, 5),    # any completion → 5 XP
]


def _evaluate_exercise(exercise: Exercise, user_answer) -> bool:
    """Factory-pattern evaluation. Routes by exercise_type.name."""
    ex_type = exercise.exercise_type.name if exercise.exercise_type else ""
    answer_data = exercise.answer_data or {}

    if ex_type == "COMPLETE_CONVERSATION":
        return str(user_answer) == str(answer_data.get("correct_option_id", ""))

    elif ex_type == "ARRANGE_WORDS":
        correct = answer_data.get("correct_sequence", [])
        if isinstance(user_answer, list):
            return [str(t) for t in user_answer] == [str(t) for t in correct]
        return False

    elif ex_type == "COMPLETE_TRANSLATION":
        correct = answer_data.get("correct_words", [])
        if isinstance(user_answer, list):
            return [w.strip().lower() for w in user_answer] == [w.strip().lower() for w in correct]
        return False

    elif ex_type == "PICTURE_MATCH":
        return str(user_answer) == str(answer_data.get("correct_option_id", ""))

    elif ex_type == "TYPE_HEAR":
        correct = answer_data.get("correct_transcription", "")
        return str(user_answer).strip().lower() == correct.strip().lower()

    elif ex_type == "LISTEN_FILL":
        correct = answer_data.get("correct_sequence_ids", [])
        if isinstance(user_answer, list):
            return [str(i) for i in user_answer] == [str(i) for i in correct]
        return False

    elif ex_type == "SPEAK_SENTENCE":
        # STT result comparison (normalised)
        expected = answer_data.get("expected_text", "")
        return str(user_answer).strip().lower() == expected.strip().lower()

    return False


class LessonService:
    def __init__(self):
        self.repository = lesson_repository
        self.exercise_repository = exercise_repository

    def get_lesson_payload(
        self, db: Session, lesson_id: uuid.UUID
    ) -> Optional[Lesson]:
        """Full lesson with exercises for client pre-fetch.
        Each exercise includes the type name but NOT answer_data.
        """
        return self.repository.get_with_exercises(db, lesson_id)

    def build_client_payload(self, lesson: Lesson) -> LessonPayload:
        """Convert ORM Lesson → LessonPayload with typed ExerciseClient items."""
        exercises: List[ExerciseClient] = []
        for ex in lesson.exercises:
            type_name = ex.exercise_type.name if ex.exercise_type else "UNKNOWN"
            exercises.append(
                ExerciseClient(
                    id=ex.id,
                    lesson_id=ex.lesson_id,
                    type=type_name,
                    question_data=ex.question_data or {},
                    answer_data=ex.answer_data or {},
                )
            )

        return LessonPayload(
            id=lesson.id,
            unit_id=lesson.unit_id,
            lesson_form_id=lesson.lesson_form_id,
            title=lesson.title,
            order_index=lesson.order_index,
            exercises=exercises,
        )

    def get_exercises_for_lesson(
        self, db: Session, lesson_id: uuid.UUID
    ) -> List[ExerciseClient]:
        """Return exercises for a lesson without answer_data (client mode)."""
        exercises = self.exercise_repository.get_by_lesson(db, lesson_id)
        result = []
        for ex in exercises:
            type_name = ex.exercise_type.name if ex.exercise_type else "UNKNOWN"
            result.append(
                ExerciseClient(
                    id=ex.id,
                    lesson_id=ex.lesson_id,
                    type=type_name,
                    question_data=ex.question_data or {},
                    answer_data=ex.answer_data or {},
                )
            )
        return result



    def submit_lesson(
        self,
        db: Session,
        user: User,
        lesson_id: uuid.UUID,
        submission: LessonSubmission,
    ) -> ProgressResponse:
        """
        Process a completed lesson submission:
        1. Calculate XP from accuracy
        2. Update hearts from submission
        3. Update streak (SQL Server, no Redis)
        4. Write UserLessonProgress
        """
        lesson = self.repository.get(db, lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

        total_answers = len(submission.answers)
        correct_answers = sum(1 for a in submission.answers if a.is_correct)
        accuracy = correct_answers / total_answers if total_answers > 0 else 0.0

        xp_earned = 5
        for threshold, xp in XP_TIERS:
            if accuracy >= threshold:
                xp_earned = xp
                break

        user.total_xp += xp_earned
        user.hearts = submission.hearts_left

        now = datetime.now(timezone.utc)
        last_activity = user.last_activity_at
        if last_activity is not None:
            if last_activity.tzinfo is None:
                last_activity = last_activity.replace(tzinfo=timezone.utc)
            delta = now - last_activity
            if delta.days == 0:
                pass
            elif delta.days == 1:
                user.current_streak += 1
            else:
                user.current_streak = 1
        else:
            user.current_streak = 1
        user.last_activity_at = now

        db.add(user)

        mistakes = total_answers - correct_answers
        progress = db.get(UserLessonProgress, (user.id, lesson_id))
        if progress:
            # Update existing record
            progress.score = max(progress.score, submission.score)
            progress.mistakes = mistakes
            progress.completed_at = now
        else:
            progress = UserLessonProgress(
                user_id=user.id,
                lesson_id=lesson_id,
                score=submission.score,
                mistakes=mistakes,
                completed_at=now,
            )
            db.add(progress)
        db.flush()

        return ProgressResponse(
            xp_earned=xp_earned,
            total_xp=user.total_xp,
            current_streak=user.current_streak,
            hearts=user.hearts,
            gems=user.gems,
        )


lesson_service = LessonService()
