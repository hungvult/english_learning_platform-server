from sqlmodel import Session
from fastapi import HTTPException, status

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.repositories.user import user_repository
from app.core.security import get_password_hash, verify_password, create_access_token


class AuthService:
    """Handles registration and login."""

    def __init__(self):
        self.repository = user_repository

    def register(self, db: Session, payload: RegisterRequest) -> TokenResponse:
        # Check duplicate email
        if self.repository.get_by_email(db, payload.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check duplicate username
        if self.repository.get_by_username(db, payload.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Create user with hashed password
        user_data = {
            "username": payload.username,
            "email": payload.email,
            "hashed_password": get_password_hash(payload.password),
        }
        user = self.repository.create(db, user_data)

        # Return JWT
        token = create_access_token(data={"sub": str(user.id)})
        return TokenResponse(access_token=token)

    def login(self, db: Session, payload: LoginRequest) -> TokenResponse:
        user = self.repository.get_by_email(db, payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = create_access_token(data={"sub": str(user.id)})
        return TokenResponse(access_token=token)


auth_service = AuthService()
