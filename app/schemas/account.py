from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
class AccountCreate(BaseModel):
    user_id: int
    name: str
    category: str
class AccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    category: str
    created_at: datetime
    model_config= ConfigDict(from_attributes=True)
class AccountBalanceResponse(BaseModel):
    account_id: int
    account_name: str
    category: str
    balance: Decimal
class AccountEntryResponse(BaseModel):
    entry_id: int
    transaction_id: int
    description: str
    entry_type: str
    amount: Decimal
    created_at: datetime