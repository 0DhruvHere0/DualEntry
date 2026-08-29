from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
class TransactionType(str, Enum):
    SALE = "SALE"
    PURCHASE = "PURCHASE"
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"
    LOAN_RECEIVED = "LOAN_RECEIVED"
    LOAN_GIVEN = "LOAN_GIVEN"
    LOAN_REPAYMENT = "LOAN_REPAYMENT"
    RECEIPT = "RECEIPT"
    PAYMENT = "PAYMENT"
    TRANSFER = "TRANSFER"
class EntryType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
class EntryCreate(BaseModel):
    account_id: int
    entry_type: EntryType
    amount: Decimal= Field(gt=0)
class TransactionCreate(BaseModel):
    user_id: int
    counterpart_id: int
    transaction_type: TransactionType
    description: str
    entries: list[EntryCreate]
class EntryResponse(BaseModel):
    id: int
    account_id: int
    entry_type: EntryType
    amount: Decimal
    model_config = ConfigDict(from_attributes=True)
class TransactionResponse(BaseModel):
    id: int
    user_id: int
    transaction_type: TransactionType
    description: str
    created_at: datetime
    entries: list[EntryResponse]
    model_config = ConfigDict(from_attributes=True)