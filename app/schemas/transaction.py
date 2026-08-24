from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
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
    description: str
    created_at: datetime
    entries: list[EntryResponse]
    model_config = ConfigDict(from_attributes=True)