"""Admin endpoints: exercise type lookup."""
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.dependencies import require_admin
from app.core.database import get_db
from app.models.exercise import ExerciseType
from app.models.user import User
from app.schemas.admin import ExerciseTypeReadAdmin

router = APIRouter()


@router.get("/", response_model=List[ExerciseTypeReadAdmin], summary="List exercise types")
def list_exercise_types(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.exec(select(ExerciseType)).all()
