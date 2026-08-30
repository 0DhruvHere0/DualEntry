from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session
from decimal import Decimal
from app.database.dependency import get_db
from app.models.account import Account
from app.models.entry import Entry
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountBalanceResponse,
    AccountEntryResponse,
    AccountLedgerResponse,
    TrialBalanceAccountResponse,
    TrialBalanceResponse,
)
router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)
@router.post(
    "/",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
) -> Account:
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
        select(Account).where(
            Account.id == account_id
        )
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
        .where(
            Entry.account_id == account_id
        )
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
        select(Account).where(
            Account.id == account_id
        )
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
        .where(
            Entry.account_id == account_id
        )
        .order_by(
            Transaction.created_at.desc()
        )
    ).mappings().all()
    return entries
@router.get(
    "/{account_id}/ledger",
    response_model=AccountLedgerResponse
)
def get_account_ledger(
    account_id: int,
    db: Session = Depends(get_db)
):
    account = db.scalar(
        select(Account).where(
            Account.id == account_id
        )
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
            Transaction.transaction_type,
            Entry.entry_type,
            Entry.amount,
            Transaction.created_at,
        )
        .join(
            Transaction,
            Entry.transaction_id == Transaction.id
        )
        .where(
            Entry.account_id == account_id
        )
        .order_by(
            Transaction.created_at.asc(),
            Entry.id.asc()
        )
    ).mappings().all()
    running_balance = 0
    ledger_entries = []
    for entry in entries:
        debit = (
            entry["amount"]
            if entry["entry_type"] == "DEBIT"
            else Decimal("0.00")
        )
        credit = (
            entry["amount"]
            if entry["entry_type"] == "CREDIT"
            else Decimal("0.00")
        )
        if account.category in ("Asset", "Expense"):
            running_balance += debit - credit
        else:
            running_balance += credit - debit
        ledger_entries.append({
            "entry_id": entry["entry_id"],
            "transaction_id": entry["transaction_id"],
            "description": entry["description"],
            "transaction_type": entry["transaction_type"],
            "entry_type": entry["entry_type"],
            "amount": entry["amount"],
            "debit": debit,
            "credit": credit,
            "balance": running_balance,
            "created_at": entry["created_at"],
        })
    return {
        "account_id": account.id,
        "account_name": account.name,
        "category": account.category,
        "entries": ledger_entries,
    }
@router.get(
    "/{user_id}/trial-balance",
    response_model=TrialBalanceResponse
)
def get_trial_balance(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(
            User.id == user_id
        )
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    accounts = db.scalars(
        select(Account)
        .where(
            Account.user_id == user_id
        )
        .order_by(
            Account.id
        )
    ).all()
    trial_balance_accounts = []
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")
    for account in accounts:
        debit = db.scalar(
            select(
                func.coalesce(
                    func.sum(Entry.amount),
                    0
                )
            )
            .where(
                Entry.account_id == account.id,
                Entry.entry_type == "DEBIT"
            )
        )
        credit = db.scalar(
            select(
                func.coalesce(
                    func.sum(Entry.amount),
                    0
                )
            )
            .where(
                Entry.account_id == account.id,
                Entry.entry_type == "CREDIT"
            )
        )
        debit = Decimal(debit)
        credit = Decimal(credit)
        trial_balance_accounts.append(
            {
                "account_id": account.id,
                "account_name": account.name,
                "category": account.category,
                "debit": debit,
                "credit": credit,
            }
        )
        total_debit += debit
        total_credit += credit
    return {
        "accounts": trial_balance_accounts,
        "total_debit": total_debit,
        "total_credit": total_credit,
    }