from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.dependency import get_db
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse
router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)
@router.post("/",response_model=AccountResponse,status_code=status.HTTP_201_CREATED,)
def create_account(account: AccountCreate,db: Session = Depends(get_db),) -> Account:
    existing_account = (
        db.query(Account)
        .filter(Account.name == account.name)
        .first()
    )
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this name already exists.",
        )
    new_account = Account(
        name=account.name,
        category=account.category,
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account