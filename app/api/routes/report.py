from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session
from app.database.dependency import get_db
from app.models.account import Account
from app.models.entry import Entry
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.account import (
    TrialBalanceAccountResponse,
    TrialBalanceResponse,
    AccountLedgerEntryResponse,
    AccountLedgerResponse
)
from app.schemas.report import (
    IncomeStatementItem,
    IncomeStatementResponse,
    BalanceSheetItem,
    BalanceSheetResponse,
)
from app.services.excel_export import (
    create_financial_report_excel
)
router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)
@router.get(
    "/trial-balance/{user_id}",
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
        .order_by(
            Account.id
        )
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
@router.get(
    "/account-ledger/{account_id}",
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
    rows = db.execute(
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
    ).all()
    ledger_entries = []
    balance = 0
    for row in rows:
        if row.entry_type == "DEBIT":
            debit = row.amount
            credit = 0
            if account.category in ["Asset", "Expense"]:
                balance += row.amount
            else:
                balance -= row.amount
        else:
            debit = 0
            credit = row.amount
            if account.category in ["Asset", "Expense"]:
                balance -= row.amount
            else:
                balance += row.amount
        ledger_entries.append(
            AccountLedgerEntryResponse(
                entry_id=row.entry_id,
                transaction_id=row.transaction_id,
                description=row.description,
                transaction_type=row.transaction_type,
                entry_type=row.entry_type,
                amount=row.amount,
                debit=debit,
                credit=credit,
                balance=balance,
                created_at=row.created_at,
            )
        )
    return AccountLedgerResponse(
        account_id=account.id,
        account_name=account.name,
        category=account.category,
        entries=ledger_entries,
    )
@router.get(
    "/income-statement/{user_id}",
    response_model=IncomeStatementResponse
)
def get_income_statement(
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
    rows = db.execute(
        select(
            Account.id.label("account_id"),
            Account.name.label("account_name"),
            Account.category.label("category"),
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
        )
        .outerjoin(
            Entry,
            Entry.account_id == Account.id
        )
        .where(
            Account.user_id == user_id,
            Account.category.in_(
                ["Income", "Expense"]
            )
        )
        .group_by(
            Account.id,
            Account.name,
            Account.category
        )
        .order_by(
            Account.id
        )
    ).all()
    income = []
    expenses = []
    for row in rows:
        if row.category == "Income":
            amount = row.credit - row.debit
            income.append(
                IncomeStatementItem(
                    account_id=row.account_id,
                    account_name=row.account_name,
                    amount=amount,
                )
            )
        elif row.category == "Expense":
            amount = row.debit - row.credit
            expenses.append(
                IncomeStatementItem(
                    account_id=row.account_id,
                    account_name=row.account_name,
                    amount=amount,
                )
            )
    total_income = sum(
        item.amount
        for item in income
    )
    total_expenses = sum(
        item.amount
        for item in expenses
    )
    net_income = (
        total_income - total_expenses
    )
    return IncomeStatementResponse(
        income=income,
        expenses=expenses,
        total_income=total_income,
        total_expenses=total_expenses,
        net_income=net_income,
    )
@router.get(
    "/balance-sheet/{user_id}",
    response_model=BalanceSheetResponse
)
def get_balance_sheet(
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
            Account.user_id == user_id,
            Account.category.in_(
                ["Asset", "Liability", "Equity"]
            )
        )
        .group_by(
            Account.id,
            Account.name,
            Account.category
        )
        .order_by(
            Account.id
        )
    ).all()
    assets = []
    liabilities = []
    equity = []
    for row in rows:
        if row.category == "Asset":
            amount = row.debit - row.credit
            assets.append(
                BalanceSheetItem(
                    account_id=row.account_id,
                    account_name=row.account_name,
                    amount=amount,
                )
            )
        elif row.category == "Liability":
            amount = row.credit - row.debit
            liabilities.append(
                BalanceSheetItem(
                    account_id=row.account_id,
                    account_name=row.account_name,
                    amount=amount,
                )
            )
        elif row.category == "Equity":
            amount = row.credit - row.debit
            equity.append(
                BalanceSheetItem(
                    account_id=row.account_id,
                    account_name=row.account_name,
                    amount=amount,
                )
            )
    total_assets = sum(
        item.amount
        for item in assets
    )
    total_liabilities = sum(
        item.amount
        for item in liabilities
    )
    total_equity = sum(
        item.amount
        for item in equity
    )
    income_rows = db.execute(
        select(
            Account.category.label("category"),
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
        )
        .outerjoin(
            Entry,
            Entry.account_id == Account.id
        )
        .where(
            Account.user_id == user_id,
            Account.category.in_(
                ["Income", "Expense"]
            )
        )
        .group_by(
            Account.category
        )
    ).all()
    total_income = 0
    total_expenses = 0
    for row in income_rows:
        if row.category == "Income":
            total_income += (
                row.credit - row.debit
            )
        elif row.category == "Expense":
            total_expenses += (
                row.debit - row.credit
            )
    current_profit = (
        total_income - total_expenses
    )
    if current_profit != 0:
        equity.append(
            BalanceSheetItem(
                account_id=None,
                account_name="Current Profit",
                amount=current_profit,
            )
        )
        total_equity += current_profit
    total_liabilities_and_equity = (
        total_liabilities + total_equity
    )
    return BalanceSheetResponse(
        assets=assets,
        liabilities=liabilities,
        equity=equity,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        total_equity=total_equity,
        total_liabilities_and_equity=(
            total_liabilities_and_equity
        ),
    )
@router.get(
    "/export/{user_id}"
)
def export_financial_report(
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
    trial_balance = get_trial_balance(
        user_id=user_id,
        db=db
    )
    income_statement = get_income_statement(
        user_id=user_id,
        db=db
    )
    balance_sheet = get_balance_sheet(
        user_id=user_id,
        db=db
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
    ledgers = []
    for account in accounts:
        ledger = get_account_ledger(
            account_id=account.id,
            db=db
        )
        ledgers.append(ledger)
    excel_file = create_financial_report_excel(
        trial_balance=trial_balance,
        ledgers=ledgers,
        income_statement=income_statement,
        balance_sheet=balance_sheet,
    )
    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="financial_report_'
                f'{user_id}.xlsx"'
            )
        }
    )