from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import Session, select
import uuid

from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.models.unit import Unit
from app.schemas.admin import UnitCreate, UnitUpdate, UnitReadAdmin

router = APIRouter()


@router.get("/", response_model=List[UnitReadAdmin], summary="List units")
def list_units(
    course_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """List all units, optionally filtered by course_id."""
    stmt = select(Unit).order_by(Unit.id)
    if course_id:
        stmt = stmt.where(Unit.course_id == course_id)
    return db.exec(stmt.offset(skip).limit(limit)).all()


@router.post("/", response_model=UnitReadAdmin, status_code=status.HTTP_201_CREATED, summary="Create unit")
def create_unit(
    payload: UnitCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    unit = Unit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.get("/{unit_id}", response_model=UnitReadAdmin, summary="Get unit")
def get_unit(
    unit_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    unit = db.get(Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    return unit


@router.patch("/{unit_id}", response_model=UnitReadAdmin, summary="Update unit")
def update_unit(
    unit_id: uuid.UUID,
    payload: UnitUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    unit = db.get(Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(unit, field, value)
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete unit")
def delete_unit(
    unit_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    unit = db.get(Unit, unit_id)
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    db.delete(unit)
    db.commit()


@router.post("/swap-order", response_model=List[UnitReadAdmin], summary="Swap order_index between two units")
def swap_unit_order(
    id_a: uuid.UUID = Body(...),
    id_b: uuid.UUID = Body(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Swap the order_index values of two units atomically."""
    unit_a = db.get(Unit, id_a)
    unit_b = db.get(Unit, id_b)
    if not unit_a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unit {id_a} not found")
    if not unit_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unit {id_b} not found")

    unit_a.order_index, unit_b.order_index = unit_b.order_index, unit_a.order_index
    db.add(unit_a)
    db.add(unit_b)
    db.commit()
    db.refresh(unit_a)
    db.refresh(unit_b)
    return [unit_a, unit_b]
