import uuid
from collections.abc import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.models.course import Course
from app.models.exercise import ExerciseType
from app.models.lesson import Lesson, LessonForm
from app.models.unit import Unit
from app.models.user import User


@pytest.fixture(name="engine")
def engine_fixture():
    """Create in-memory SQLite engine with StaticPool for thread-safe test isolation."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Provide a database session pre-populated with standard ExerciseTypes and LessonForms."""
    with Session(engine) as session:
        # Seed 7 canonical exercise types
        exercise_type_names = [
            "COMPLETE_CONVERSATION",
            "ARRANGE_WORDS",
            "COMPLETE_TRANSLATION",
            "PICTURE_MATCH",
            "TYPE_HEAR",
            "LISTEN_FILL",
            "SPEAK_SENTENCE",
        ]
        for name in exercise_type_names:
            session.add(ExerciseType(id=uuid.uuid4(), name=name))

        # Seed standard lesson forms
        lesson_form_names = ["normal", "review", "test"]
        for name in lesson_form_names:
            session.add(LessonForm(id=uuid.uuid4(), name=name))

        session.commit()
        yield session


@pytest.fixture(name="exercise_types")
def exercise_types_fixture(session: Session) -> dict[str, ExerciseType]:
    """Return dictionary mapping exercise type name to ExerciseType model instance."""
    types = session.exec(select(ExerciseType)).all()
    return {t.name: t for t in types}


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """Return a fresh default test user."""
    user = User(
        id=uuid.uuid4(),
        username="learner_test",
        email="learner@example.com",
        hashed_password="hashed_test_password",
        is_admin=False,
        total_xp=0,
        hearts=5,
        gems=0,
        current_streak=0,
        last_activity_at=None,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_lesson")
def test_lesson_fixture(session: Session) -> Lesson:
    """Return a test lesson linked with a Course and Unit."""
    course = Course(
        id=uuid.uuid4(),
        title="Tiếng Anh A1",
        expected_cefr_level="A1",
    )
    session.add(course)
    session.flush()

    unit = Unit(
        id=uuid.uuid4(),
        course_id=course.id,
        title="Unit 1: Greetings",
        order_index=1,
    )
    session.add(unit)
    session.flush()

    lesson_form = session.exec(select(LessonForm)).first()
    assert lesson_form is not None

    lesson = Lesson(
        id=uuid.uuid4(),
        unit_id=unit.id,
        lesson_form_id=lesson_form.id,
        title="Lesson 1: Hello & Goodbye",
        order_index=1,
    )
    session.add(lesson)
    session.commit()
    session.refresh(lesson)
    return lesson
