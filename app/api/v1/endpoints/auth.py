from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth import auth_service

router = APIRouter()

from fastapi import Response


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Create a new account and return a JWT."""
    return auth_service.register(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Authenticate and return a JWT."""
    token = auth_service.login(db, payload)
    response.set_cookie(key="access_token", value=token.access_token, httponly=True, samesite="lax")
    return token


@router.post("/logout")
def logout(response: Response):
    """Clear the authentication cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}
