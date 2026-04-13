from sqlmodel import Session, create_engine
from app.core.config import get_settings

# Lazy engine initialization to avoid import-time failures
# when ODBC drivers aren't available yet
_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.DATABASE_URL,
            echo=True,
        )
    return _engine


def get_db():
    """Dependency that yields a database session with commit/rollback."""
    with Session(_get_engine()) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
