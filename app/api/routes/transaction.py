from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.dependency import get_db
from app.models.transaction import Transaction
from app.models.entry import Entry
from app.models.user import User
from app.models.account import Account
from app.models.counterpart import Counterpart
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    EntryType,
    TransactionType,
)
router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)
@router.post(
    "/",
    response_model=TransactionResponse
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(
            User.id == transaction_data.user_id
        )
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    counterpart = db.scalar(
        select(User).where(
            User.id == transaction_data.counterpart_id
        )
    )
    if counterpart is None:
        raise HTTPException(
            status_code=404,
            detail="Counterpart user not found"
        )
    if transaction_data.user_id == transaction_data.counterpart_id:
        raise HTTPException(
            status_code=400,
            detail="User and counterpart cannot be the same"
        )
    counterpart_relationship = db.scalar(
        select(Counterpart).where(
            Counterpart.user_id == transaction_data.user_id,
            Counterpart.counterpart_id == transaction_data.counterpart_id,
        )
    )
    if counterpart_relationship is None:
        raise HTTPException(
            status_code=400,
            detail="Counterpart relationship does not exist"
        )
    if transaction_data.transaction_type == TransactionType.LOAN_RECEIVED:
        if counterpart_relationship.relationship_type != "LENDER":
            raise HTTPException(
                status_code=400,
                detail=(
                    "LOAN_RECEIVED requires counterpart "
                    "relationship to be LENDER"
                )
            )
    if transaction_data.transaction_type == TransactionType.LOAN_GIVEN:
        if counterpart_relationship.relationship_type != "BORROWER":
            raise HTTPException(
                status_code=400,
                detail=(
                    "LOAN_GIVEN requires counterpart "
                    "relationship to be BORROWER"
                )
            )
    accounts = {}
    for entry_data in transaction_data.entries:
        account = db.scalar(
            select(Account).where(
                Account.id == entry_data.account_id
            )
        )
        if account is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Account {entry_data.account_id} not found"
                )
            )
        if account.user_id != transaction_data.user_id:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Account {entry_data.account_id} "
                    "does not belong to this user"
                )
            )
        accounts[entry_data.account_id] = account
    if not transaction_data.entries:
        raise HTTPException(
            status_code=400,
            detail="Transaction must contain at least one entry"
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
    if debit_total == 0 or credit_total == 0:
        raise HTTPException(
            status_code=400,
            detail="Transaction must contain both debit and credit entries"
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
    if transaction_data.transaction_type == TransactionType.SALE:
        for entry_data in transaction_data.entries:
            account = accounts[entry_data.account_id]
            if entry_data.entry_type == EntryType.DEBIT:
                if account.category != "Asset":
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "SALE debit entry must use "
                            "an Asset account"
                        )
                    )
            elif entry_data.entry_type == EntryType.CREDIT:
                if account.category != "Income":
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "SALE credit entry must use "
                            "an Income account"
                        )
                    )
    if transaction_data.transaction_type == TransactionType.PURCHASE:
        for entry_data in transaction_data.entries:
            account = accounts[entry_data.account_id]
            if entry_data.entry_type == EntryType.DEBIT:
                if account.category not in ("Asset", "Expense"):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "PURCHASE debit entry must use "
                            "an Asset or Expense account"
                        )
                    )
            elif entry_data.entry_type == EntryType.CREDIT:
                if account.category not in ("Asset", "Liability"):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "PURCHASE credit entry must use "
                            "an Asset or Liability account"
                        )
                    )
    if transaction_data.transaction_type == TransactionType.EXPENSE:
        for entry_data in transaction_data.entries:
            account = accounts[entry_data.account_id]
            if entry_data.entry_type == EntryType.DEBIT:
                if account.category != "Expense":
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "EXPENSE debit entry must use "
                            "an Expense account"
                        )
                    )
            elif entry_data.entry_type == EntryType.CREDIT:
                if account.category not in ("Asset", "Liability"):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "EXPENSE credit entry must use "
                            "an Asset or Liability account"
                        )
                    )
    if transaction_data.transaction_type == TransactionType.INCOME:
        for entry_data in transaction_data.entries:
            account = accounts[entry_data.account_id]
            if entry_data.entry_type == EntryType.DEBIT:
                if account.category != "Asset":
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "INCOME debit entry must use "
                            "an Asset account"
                        )
                    )
            elif entry_data.entry_type == EntryType.CREDIT:
                if account.category != "Income":
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "INCOME credit entry must use "
                            "an Income account"
                        )
                    )
    transaction = Transaction(
        user_id=transaction_data.user_id,
        counterpart_id=transaction_data.counterpart_id,
        transaction_type=transaction_data.transaction_type.value,
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
        select(User).where(
            User.id == user_id
        )
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    transactions = db.scalars(
        select(Transaction)
        .where(
            Transaction.user_id == user_id
        )
        .order_by(
            Transaction.created_at.desc()
        )
    ).all()
    return transactions
@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse
)
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