from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session
from app.database.dependency import get_db
from app.models.account import Account
from app.models.entry import Entry
from app.models.user import User
from app.schemas.account import (
    AccountCreate, 
    AccountResponse, 
    AccountBalanceResponse, 
    AccountEntryResponse,
    TrialBalanceAccountResponse,
    TrialBalanceResponse
)
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
        category=account.category.value,
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
@router.get(
    "/user/{user_id}/trial-balance",
    response_model=TrialBalanceResponse
)
def get_trial_balance(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(User.id == user_id)
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    rows = db.execute(
        select(
            Account.id.label("account_id"),
            Account.name.label("account_name"),
            Account.category.label("category"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            Entry.entry_type == "DEBIT",
                            Entry.amount
                        ),
                        else_=0
                    )
                ),
                0
            ).label("debit"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            Entry.entry_type == "CREDIT",
                            Entry.amount
                        ),
                        else_=0
                    )
                ),
                0
            ).label("credit"),
        )
        .outerjoin(
            Entry,
            Entry.account_id == Account.id
        )
        .where(
            Account.user_id == user_id
        )
        .group_by(
            Account.id,
            Account.name,
            Account.category
        )
        .order_by(Account.id)
    ).all()
    accounts = [
        TrialBalanceAccountResponse(
            account_id=row.account_id,
            account_name=row.account_name,
            category=row.category,
            debit=row.debit,
            credit=row.credit,
        )
        for row in rows
    ]
    total_debit = sum(
        account.debit
        for account in accounts
    )
    total_credit = sum(
        account.credit
        for account in accounts
    )
    return TrialBalanceResponse(
        accounts=accounts,
        total_debit=total_debit,
        total_credit=total_credit,
    )