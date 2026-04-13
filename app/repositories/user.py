from typing import Optional
from sqlmodel import Session, select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return db.exec(statement).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        return db.exec(statement).first()


user_repository = UserRepository()
