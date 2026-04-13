from typing import Optional
from sqlmodel import Session
import uuid

from app.models.user import User
from app.schemas.user import UserUpdate
from app.repositories.user import user_repository


class UserService:
    def __init__(self):
        self.repository = user_repository

    def get_profile(self, db: Session, user_id: uuid.UUID) -> Optional[User]:
        return self.repository.get(db, user_id)

    def update_profile(
        self, db: Session, user: User, payload: UserUpdate
    ) -> User:
        update_data = payload.model_dump(exclude_unset=True)
        return self.repository.update(db, user, update_data)


user_service = UserService()
