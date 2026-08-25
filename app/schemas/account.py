from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from enum import Enum
class AccountCategory(str, Enum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    EQUITY = "Equity"
    INCOME = "Income"
    EXPENSE = "Expense"
class AccountCreate(BaseModel):
    user_id: int
    name: str
    category: AccountCategory
class AccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category: AccountCategory
    created_at: datetime
    model_config= ConfigDict(from_attributes=True)
class AccountBalanceResponse(BaseModel):
    account_id: int
    account_name: str
    category: AccountCategory
    balance: Decimal
class AccountEntryResponse(BaseModel):
    entry_id: int
    transaction_id: int
    description: str
    entry_type: str
    amount: Decimal
    created_at: datetime
class TrialBalanceAccountResponse(BaseModel):
    account_id: int
    account_name: str
    category: AccountCategory
    debit: Decimal
    credit: Decimal
class TrialBalanceResponse(BaseModel):
    accounts: list[TrialBalanceAccountResponse]
    total_debit: Decimal
    total_credit: Decimal