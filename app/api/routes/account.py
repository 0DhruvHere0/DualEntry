from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session
from app.database.dependency import get_db
from app.models.account import Account
from app.models.entry import Entry
from app.schemas.account import AccountCreate, AccountResponse, AccountBalanceResponse, AccountEntryResponse
from app.models.transaction import Transaction
router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)
@router.post("/",response_model=AccountResponse,status_code=status.HTTP_201_CREATED,)
def create_account(account: AccountCreate,db: Session = Depends(get_db),) -> Account:
    existing_account = (
        db.query(Account)
        .filter(
            Account.user_id == account.user_id,
            Account.name == account.name
        )
        .first()
    )
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this name already exists.",
        )
    new_account = Account(
        user_id=account.user_id,
        name=account.name,
        category=account.category,
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account
@router.get(
    "/{account_id}/balance",
    response_model=AccountBalanceResponse
)
def get_account_balance(
    account_id: int,
    db: Session = Depends(get_db)
):
    account = db.scalar(
        select(Account).where(Account.id == account_id)
    )
    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    balance = db.scalar(
        select(
            func.coalesce(
                func.sum(
                    case(
                        (Entry.entry_type == "DEBIT", Entry.amount),
                        (Entry.entry_type == "CREDIT", -Entry.amount),
                    )
                ),
                0
            )
        )
        .where(Entry.account_id == account_id)
    )
    if account.category == "Liability":
        balance = -balance
    return {
        "account_id": account.id,
        "account_name": account.name,
        "category": account.category,
        "balance": balance,
    }
@router.get(
    "/{account_id}/entries",
    response_model=list[AccountEntryResponse]
)
def get_account_entries(
    account_id: int,
    db: Session = Depends(get_db)
):
    account = db.scalar(
        select(Account).where(Account.id == account_id)
    )
    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    entries = db.execute(
        select(
            Entry.id.label("entry_id"),
            Entry.transaction_id,
            Transaction.description,
            Entry.entry_type,
            Entry.amount,
            Transaction.created_at,
        )
        .join(
            Transaction,
            Entry.transaction_id == Transaction.id
        )
        .where(Entry.account_id == account_id)
        .order_by(Transaction.created_at.desc())
    ).mappings().all()
    return entries