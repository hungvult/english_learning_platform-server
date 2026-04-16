from typing import Optional
from sqlmodel import Session
import uuid

from app.models.user import User
from app.schemas.user import UserUpdate
from app.repositories.user import user_repository
from app.core.security import get_password_hash
from fastapi import HTTPException, status


class UserService:
    def __init__(self):
        self.repository = user_repository

    def get_profile(self, db: Session, user_id: uuid.UUID) -> Optional[User]:
        return self.repository.get(db, user_id)

    def update_profile(
        self, db: Session, user: User, payload: UserUpdate
    ) -> User:
        update_data = payload.model_dump(exclude_unset=True)

        # Handle password hashing
        if "password" in update_data:
            password = update_data.pop("password")
            update_data["hashed_password"] = get_password_hash(password)

        # Handle email uniqueness
        if "email" in update_data and update_data["email"] != user.email:
            if self.repository.get_by_email(db, update_data["email"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

        return self.repository.update(db, user, update_data)


user_service = UserService()
