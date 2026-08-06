from datetime import datetime
from pydantic import BaseModel, ConfigDict
class AccountCreate(BaseModel):
    name: str
    category: str
class AccountResponse(BaseModel):
    id: int
    name: str
    category: str
    created_at: datetime
    model_config= ConfigDict(from_attributes=True)