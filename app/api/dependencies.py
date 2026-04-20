from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session
import uuid

from app.core.database import get_db
from app.core.security import ALGORITHM
from app.core.config import get_settings
from app.repositories.user import user_repository
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _token_from_cookie(request: Request) -> str | None:
    """Extract JWT from access_token cookie.

    Accept both raw token and "Bearer <token>" formats.
    """
    raw = request.cookies.get("access_token")
    if not raw:
        return None
    if raw.startswith("Bearer "):
        return raw[7:]
    return raw


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
) -> User:
    """Decode JWT and return the authenticated user.

    Token resolution order:
    1) Authorization: Bearer <token>
    2) access_token cookie
    """
    settings = get_settings()

    resolved_token = token or _token_from_cookie(request)
    if not resolved_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(resolved_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    user = user_repository.get(db, user_id)
    if user is None:
        raise credentials_exception

    return user


def require_authenticated_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Base authenticated dependency.

    Role inheritance model: admin is also an authenticated user.
    """
    return current_user


def require_admin(
    current_user: User = Depends(require_authenticated_user),
) -> User:
    """Raise 403 if the authenticated user is not an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
