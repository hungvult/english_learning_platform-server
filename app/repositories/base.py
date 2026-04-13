from typing import Generic, TypeVar, Type, Optional, List
from sqlmodel import Session, select
import uuid

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic CRUD repository for SQLModel entities with UUID primary keys."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: uuid.UUID) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        return db.exec(statement).all()

    def create(self, db: Session, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: ModelType, update_data: dict
    ) -> ModelType:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: uuid.UUID) -> bool:
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.flush()
            return True
        return False
