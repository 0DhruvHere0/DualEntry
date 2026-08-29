from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.dependency import get_db
from app.models.counterpart import Counterpart
from app.models.user import User
from app.schemas.counterpart import (
    CounterpartCreate,
    CounterpartResponse,
)
router = APIRouter(
    prefix="/counterparts",
    tags=["Counterparts"],
)
@router.post(
    "/",
    response_model=CounterpartResponse,
    status_code=201,
)
def create_counterpart(
    counterpart_data: CounterpartCreate,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(
            User.id == counterpart_data.user_id
        )
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    counterpart = db.scalar(
        select(User).where(
            User.id == counterpart_data.counterpart_id
        )
    )
    if counterpart is None:
        raise HTTPException(
            status_code=404,
            detail="Counterpart user not found",
        )
    if (
        counterpart_data.user_id
        == counterpart_data.counterpart_id
    ):
        raise HTTPException(
            status_code=400,
            detail="User and counterpart cannot be the same",
        )
    existing_relationship = db.scalar(
        select(Counterpart).where(
            Counterpart.user_id == counterpart_data.user_id,
            Counterpart.counterpart_id
            == counterpart_data.counterpart_id,
        )
    )
    if existing_relationship is not None:
        raise HTTPException(
            status_code=400,
            detail="Counterpart relationship already exists",
        )
    new_counterpart = Counterpart(
        user_id=counterpart_data.user_id,
        counterpart_id=counterpart_data.counterpart_id,
        relationship_type=counterpart_data.relationship_type,
    )
    db.add(new_counterpart)
    db.commit()
    db.refresh(new_counterpart)
    return {
        "id": new_counterpart.id,
        "user_id": new_counterpart.user_id,
        "counterpart_id": new_counterpart.counterpart_id,
        "counterpart_name": counterpart.name,
        "relationship_type": new_counterpart.relationship_type,
        "created_at": new_counterpart.created_at,
    }
@router.get(
    "/user/{user_id}",
    response_model=list[CounterpartResponse],
)
def get_user_counterparts(
    user_id: int,
    relationship_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(User).where(User.id == user_id)
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    query = (
        select(
            Counterpart,
            User.name.label("counterpart_name"),
        )
        .join(
            User,
            User.id == Counterpart.counterpart_id,
        )
        .where(
            Counterpart.user_id == user_id
        )
    )
    if relationship_type:
        query = query.where(
            Counterpart.relationship_type
            == relationship_type
        )
    query = query.order_by(
        Counterpart.created_at.desc()
    )
    results = db.execute(query).all()
    return [
        {
            "id": counterpart.id,
            "user_id": counterpart.user_id,
            "counterpart_id": counterpart.counterpart_id,
            "counterpart_name": counterpart_name,
            "relationship_type": counterpart.relationship_type,
            "created_at": counterpart.created_at,
        }
        for counterpart, counterpart_name in results
    ]