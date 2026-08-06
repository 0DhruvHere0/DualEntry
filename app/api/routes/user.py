from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.dependency import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)
@router.post(
    "/",
    response_model=UserResponse,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    new_user = User(
        name=user.name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user