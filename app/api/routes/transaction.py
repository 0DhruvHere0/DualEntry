from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.dependency import get_db
from app.models.transaction import Transaction
from app.models.entry import Entry
from app.models.user import User
from app.models.account import Account
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    EntryType,
)
router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)
@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):
    user = db.scalar(
    select(User).where(User.id == transaction_data.user_id)
)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
    )
    for entry_data in transaction_data.entries:
        account = db.scalar(
            select(Account).where(
                Account.id == entry_data.account_id
        )
    )
    if account is None:
        raise HTTPException(
            status_code=404,
            detail=f"Account {entry_data.account_id} not found"
        )
    if account.user_id != transaction_data.user_id:
        raise HTTPException(
            status_code=403,
            detail=f"Account {entry_data.account_id} does not belong to this user"
        )
    debit_total = sum(
        entry.amount
        for entry in transaction_data.entries
        if entry.entry_type == EntryType.DEBIT
    )
    credit_total = sum(
        entry.amount
        for entry in transaction_data.entries
        if entry.entry_type == EntryType.CREDIT
    )
    if debit_total != credit_total:
        raise HTTPException(
            status_code=400,
            detail="Total debits must equal total credits"
        )
    if debit_total == 0:
        raise HTTPException(
            status_code=400,
            detail="Transaction amount must be greater than zero"
        )
    transaction = Transaction(
        user_id=transaction_data.user_id,
        counterpart_id=transaction_data.counterpart_id,
        description=transaction_data.description
    )
    db.add(transaction)
    db.flush()
    for entry_data in transaction_data.entries:
        entry = Entry(
            transaction_id=transaction.id,
            account_id=entry_data.account_id,
            entry_type=entry_data.entry_type.value,
            amount=entry_data.amount
        )
        db.add(entry)
    db.commit()
    db.refresh(transaction)
    return transaction
@router.get(
    "/user/{user_id}",
    response_model=list[TransactionResponse]
)
def get_user_transactions(
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
    transactions = db.scalars(
        select(Transaction)
        .where(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
    ).all()
    return transactions
@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id
        )
    )
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    return transaction