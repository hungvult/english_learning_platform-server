from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session
from fastapi import HTTPException, status
import uuid

from app.models.lesson import Lesson
from app.models.user import User
from app.models.user_lesson_progress import UserLessonProgress
from app.schemas.progress import LessonSubmission, ProgressResponse
from app.repositories.lesson import lesson_repository


# XP reward tiers based on accuracy percentage
XP_TIERS = [
    (1.0, 20),   # 100% accuracy → 20 XP
    (0.8, 15),   # 80%+ → 15 XP
    (0.5, 10),   # 50%+ → 10 XP
    (0.0, 5),    # any completion → 5 XP
]


class LessonService:
    def __init__(self):
        self.repository = lesson_repository

    def get_lesson_payload(
        self, db: Session, lesson_id: uuid.UUID
    ) -> Optional[Lesson]:
        """Full lesson with exercises for client pre-fetch."""
        return self.repository.get_with_exercises(db, lesson_id)

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
        # Validate lesson exists
        lesson = self.repository.get(db, lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )

        # Calculate XP
        total_answers = len(submission.answers)
        correct_answers = sum(1 for a in submission.answers if a.is_correct)
        accuracy = correct_answers / total_answers if total_answers > 0 else 0.0

        xp_earned = 5  # default
        for threshold, xp in XP_TIERS:
            if accuracy >= threshold:
                xp_earned = xp
                break

        # Update user stats
        user.total_xp += xp_earned
        user.hearts = submission.hearts_left

        # Update streak
        now = datetime.now(timezone.utc)
        if user.last_activity_at:
            delta = now - user.last_activity_at
            if delta.days == 0:
                pass  # same day, streak unchanged
            elif delta.days == 1:
                user.current_streak += 1
            else:
                user.current_streak = 1  # streak broken, restart
        else:
            user.current_streak = 1  # first activity
        user.last_activity_at = now

        db.add(user)

        # Write progress record
        mistakes = total_answers - correct_answers
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
