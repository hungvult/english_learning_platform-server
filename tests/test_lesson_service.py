import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.exercise import Exercise, ExerciseType
from app.models.lesson import Lesson
from app.models.user import User
from app.models.user_exercise_log import UserExerciseLog
from app.models.user_lesson_progress import UserLessonProgress
from app.schemas.progress import AnswerDetail, LessonSubmission
from app.services.lesson import _evaluate_exercise, lesson_service

# ---------------------------------------------------------------------------
# Streak Calculation Logic
# ---------------------------------------------------------------------------


def test_streak_first_activity(session: Session, test_user: User, test_lesson: Lesson):
    """When user has no prior activity, current_streak becomes 1."""
    test_user.last_activity_at = None
    test_user.current_streak = 0
    session.add(test_user)
    session.commit()

    sub = LessonSubmission(
        answers=[AnswerDetail(exercise_id=uuid.uuid4(), user_answer="A", is_correct=True)],
        score=100,
        hearts_left=5,
    )
    res = lesson_service.submit_lesson(session, test_user, test_lesson.id, sub)
    assert res.current_streak == 1
    assert test_user.current_streak == 1
    assert test_user.last_activity_at is not None


def test_streak_consecutive_day_increments(session: Session, test_user: User, test_lesson: Lesson):
    """When activity happens on consecutive calendar day, current_streak increments by 1."""
    yesterday = datetime.now(UTC) - timedelta(days=1)
    test_user.last_activity_at = yesterday
    test_user.current_streak = 3
    session.add(test_user)
    session.commit()

    sub = LessonSubmission(
        answers=[AnswerDetail(exercise_id=uuid.uuid4(), user_answer="A", is_correct=True)],
        score=100,
        hearts_left=5,
    )
    res = lesson_service.submit_lesson(session, test_user, test_lesson.id, sub)
    assert res.current_streak == 4
    assert test_user.current_streak == 4


def test_streak_same_day_unchanged(session: Session, test_user: User, test_lesson: Lesson):
    """Multiple submissions on the same calendar day keep streak unchanged."""
    earlier_today = datetime.now(UTC) - timedelta(hours=2)
    test_user.last_activity_at = earlier_today
    test_user.current_streak = 5
    session.add(test_user)
    session.commit()

    sub = LessonSubmission(
        answers=[AnswerDetail(exercise_id=uuid.uuid4(), user_answer="A", is_correct=True)],
        score=100,
        hearts_left=4,
    )
    res = lesson_service.submit_lesson(session, test_user, test_lesson.id, sub)
    assert res.current_streak == 5
    assert test_user.current_streak == 5


def test_streak_same_day_zero_streak_initialized(
    session: Session, test_user: User, test_lesson: Lesson
):
    """If streak was 0 and activity happens today, streak becomes 1."""
    earlier_today = datetime.now(UTC) - timedelta(hours=1)
    test_user.last_activity_at = earlier_today
    test_user.current_streak = 0
    session.add(test_user)
    session.commit()

    sub = LessonSubmission(
        answers=[AnswerDetail(exercise_id=uuid.uuid4(), user_answer="A", is_correct=True)],
        score=100,
        hearts_left=5,
    )
    res = lesson_service.submit_lesson(session, test_user, test_lesson.id, sub)
    assert res.current_streak == 1


def test_streak_missed_day_resets_to_one(session: Session, test_user: User, test_lesson: Lesson):
    """When more than 1 calendar day is missed, streak resets to 1."""
    two_days_ago = datetime.now(UTC) - timedelta(days=2)
    test_user.last_activity_at = two_days_ago
    test_user.current_streak = 10
    session.add(test_user)
    session.commit()

    sub = LessonSubmission(
        answers=[AnswerDetail(exercise_id=uuid.uuid4(), user_answer="A", is_correct=True)],
        score=100,
        hearts_left=5,
    )
    res = lesson_service.submit_lesson(session, test_user, test_lesson.id, sub)
    assert res.current_streak == 1
    assert test_user.current_streak == 1


# ---------------------------------------------------------------------------
# XP Accuracy Tiers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("correct_count", "total_count", "expected_xp"),
    [
        (5, 5, 20),  # 100% accuracy -> 20 XP
        (1, 1, 20),  # 100% accuracy -> 20 XP
        (4, 5, 15),  # 80% accuracy -> 15 XP
        (9, 10, 15),  # 90% accuracy -> 15 XP
        (3, 5, 10),  # 60% accuracy -> 10 XP
        (1, 2, 10),  # 50% accuracy -> 10 XP
        (2, 5, 5),  # 40% accuracy -> 5 XP
        (0, 5, 5),  # 0% accuracy -> 5 XP
        (0, 0, 5),  # Empty submission -> 5 XP
    ],
)
def test_xp_accuracy_tiers(
    session: Session,
    test_user: User,
    test_lesson: Lesson,
    correct_count: int,
    total_count: int,
    expected_xp: int,
):
    initial_xp = test_user.total_xp
    answers = []
    for i in range(total_count):
        answers.append(
            AnswerDetail(
                exercise_id=uuid.uuid4(),
                user_answer=f"ans_{i}",
                is_correct=(i < correct_count),
            )
        )

    sub = LessonSubmission(answers=answers, score=80, hearts_left=4)
    res = lesson_service.submit_lesson(session, test_user, test_lesson.id, sub)

    assert res.xp_earned == expected_xp
    assert res.total_xp == initial_xp + expected_xp
    assert test_user.total_xp == initial_xp + expected_xp


# ---------------------------------------------------------------------------
# submit_lesson Logic
# ---------------------------------------------------------------------------


def test_submit_lesson_non_existent_lesson_raises_404(session: Session, test_user: User):
    sub = LessonSubmission(answers=[], score=0, hearts_left=5)
    with pytest.raises(HTTPException) as exc_info:
        lesson_service.submit_lesson(session, test_user, uuid.uuid4(), sub)
    assert exc_info.value.status_code == 404
    assert "Lesson not found" in exc_info.value.detail


def test_submit_lesson_persists_progress_and_logs(
    session: Session, test_user: User, test_lesson: Lesson
):
    """Verify submit_lesson records UserLessonProgress and UserExerciseLog."""
    ex_id_1 = uuid.uuid4()
    ex_id_2 = uuid.uuid4()
    answers = [
        AnswerDetail(exercise_id=ex_id_1, user_answer="hello", is_correct=True),
        AnswerDetail(exercise_id=ex_id_2, user_answer="bye", is_correct=False),
    ]
    sub = LessonSubmission(
        answers=answers,
        score=75,
        hearts_left=3,
    )

    res = lesson_service.submit_lesson(session, test_user, test_lesson.id, sub)

    # Validate response
    assert res.hearts == 3
    assert res.gems == 0
    assert res.xp_earned == 10  # 1/2 = 50% -> 10 XP
    assert res.total_xp == 10

    # Validate UserLessonProgress in database
    progress = session.exec(
        select(UserLessonProgress).where(
            UserLessonProgress.user_id == test_user.id,
            UserLessonProgress.lesson_id == test_lesson.id,
        )
    ).first()
    assert progress is not None
    assert progress.score == 75

    # Validate UserExerciseLog in database
    logs = session.exec(
        select(UserExerciseLog).where(
            UserExerciseLog.user_id == test_user.id,
            UserExerciseLog.lesson_id == test_lesson.id,
        )
    ).all()
    assert len(logs) == 2
    log_map = {str(log_item.exercise_id): log_item for log_item in logs}
    assert str(ex_id_1) in log_map
    assert log_map[str(ex_id_1)].is_correct is True
    assert log_map[str(ex_id_1)].user_answer == "hello"
    assert str(ex_id_2) in log_map
    assert log_map[str(ex_id_2)].is_correct is False
    assert log_map[str(ex_id_2)].user_answer == "bye"


def test_submit_lesson_updates_existing_progress_max_score(
    session: Session, test_user: User, test_lesson: Lesson
):
    """When retaking a lesson, highest score should be preserved."""
    # First attempt with score 90
    sub1 = LessonSubmission(
        answers=[AnswerDetail(exercise_id=uuid.uuid4(), user_answer="A", is_correct=True)],
        score=90,
        hearts_left=5,
    )
    lesson_service.submit_lesson(session, test_user, test_lesson.id, sub1)

    # Second attempt with lower score 70
    sub2 = LessonSubmission(
        answers=[AnswerDetail(exercise_id=uuid.uuid4(), user_answer="A", is_correct=False)],
        score=70,
        hearts_left=4,
    )
    lesson_service.submit_lesson(session, test_user, test_lesson.id, sub2)

    progress = session.exec(
        select(UserLessonProgress).where(
            UserLessonProgress.user_id == test_user.id,
            UserLessonProgress.lesson_id == test_lesson.id,
        )
    ).first()
    assert progress is not None
    assert progress.score == 90  # Max preserved

    # Third attempt with higher score 100
    sub3 = LessonSubmission(
        answers=[AnswerDetail(exercise_id=uuid.uuid4(), user_answer="A", is_correct=True)],
        score=100,
        hearts_left=5,
    )
    lesson_service.submit_lesson(session, test_user, test_lesson.id, sub3)

    session.refresh(progress)
    assert progress.score == 100


def test_submit_lesson_clamps_negative_hearts(
    session: Session, test_user: User, test_lesson: Lesson
):
    """Hearts should be clamped to 0 minimum."""
    sub = LessonSubmission(
        answers=[AnswerDetail(exercise_id=uuid.uuid4(), user_answer="A", is_correct=False)],
        score=0,
        hearts_left=-2,
    )
    res = lesson_service.submit_lesson(session, test_user, test_lesson.id, sub)
    assert res.hearts == 0
    assert test_user.hearts == 0


# ---------------------------------------------------------------------------
# Exercise Evaluation Engine (_evaluate_exercise)
# ---------------------------------------------------------------------------


def test_evaluate_complete_conversation(exercise_types: dict[str, ExerciseType]):
    ex = Exercise(
        id=uuid.uuid4(),
        lesson_id=uuid.uuid4(),
        exercise_type_id=exercise_types["COMPLETE_CONVERSATION"].id,
        exercise_type=exercise_types["COMPLETE_CONVERSATION"],
        answer_data={"correct_option_id": "opt_2"},
    )
    assert _evaluate_exercise(ex, "opt_2") is True
    assert _evaluate_exercise(ex, "opt_1") is False


def test_evaluate_arrange_words(exercise_types: dict[str, ExerciseType]):
    ex = Exercise(
        id=uuid.uuid4(),
        lesson_id=uuid.uuid4(),
        exercise_type_id=exercise_types["ARRANGE_WORDS"].id,
        exercise_type=exercise_types["ARRANGE_WORDS"],
        answer_data={"correct_sequence": ["I", "love", "coffee"]},
    )
    assert _evaluate_exercise(ex, ["I", "love", "coffee"]) is True
    assert _evaluate_exercise(ex, ["I", "coffee", "love"]) is False
    assert _evaluate_exercise(ex, "invalid_scalar") is False


def test_evaluate_complete_translation(exercise_types: dict[str, ExerciseType]):
    ex = Exercise(
        id=uuid.uuid4(),
        lesson_id=uuid.uuid4(),
        exercise_type_id=exercise_types["COMPLETE_TRANSLATION"].id,
        exercise_type=exercise_types["COMPLETE_TRANSLATION"],
        answer_data={"correct_words": ["Good", "morning"]},
    )
    assert _evaluate_exercise(ex, ["good", "  morning "]) is True
    assert _evaluate_exercise(ex, ["bad", "morning"]) is False
    assert _evaluate_exercise(ex, "scalar") is False


def test_evaluate_picture_match(exercise_types: dict[str, ExerciseType]):
    ex = Exercise(
        id=uuid.uuid4(),
        lesson_id=uuid.uuid4(),
        exercise_type_id=exercise_types["PICTURE_MATCH"].id,
        exercise_type=exercise_types["PICTURE_MATCH"],
        answer_data={"correct_option_id": "img_cat"},
    )
    assert _evaluate_exercise(ex, "img_cat") is True
    assert _evaluate_exercise(ex, "img_dog") is False


def test_evaluate_type_hear(exercise_types: dict[str, ExerciseType]):
    ex = Exercise(
        id=uuid.uuid4(),
        lesson_id=uuid.uuid4(),
        exercise_type_id=exercise_types["TYPE_HEAR"].id,
        exercise_type=exercise_types["TYPE_HEAR"],
        answer_data={"correct_transcription": "See you later."},
    )
    assert _evaluate_exercise(ex, "  see you later. ") is True
    assert _evaluate_exercise(ex, "Goodbye") is False


def test_evaluate_listen_fill(exercise_types: dict[str, ExerciseType]):
    ex = Exercise(
        id=uuid.uuid4(),
        lesson_id=uuid.uuid4(),
        exercise_type_id=exercise_types["LISTEN_FILL"].id,
        exercise_type=exercise_types["LISTEN_FILL"],
        answer_data={"correct_sequence_ids": ["w1", "w2", "w3"]},
    )
    assert _evaluate_exercise(ex, ["w1", "w2", "w3"]) is True
    assert _evaluate_exercise(ex, ["w1", "w3", "w2"]) is False
    assert _evaluate_exercise(ex, "not_a_list") is False


def test_evaluate_speak_sentence(exercise_types: dict[str, ExerciseType]):
    ex = Exercise(
        id=uuid.uuid4(),
        lesson_id=uuid.uuid4(),
        exercise_type_id=exercise_types["SPEAK_SENTENCE"].id,
        exercise_type=exercise_types["SPEAK_SENTENCE"],
        answer_data={"expected_text": "Nice to meet you"},
    )
    assert _evaluate_exercise(ex, " nice to meet you ") is True
    assert _evaluate_exercise(ex, "Hello world") is False


def test_evaluate_unknown_exercise_type():
    ex = Exercise(
        id=uuid.uuid4(),
        lesson_id=uuid.uuid4(),
        exercise_type_id=uuid.uuid4(),
        exercise_type=None,
        answer_data={},
    )
    assert _evaluate_exercise(ex, "anything") is False
