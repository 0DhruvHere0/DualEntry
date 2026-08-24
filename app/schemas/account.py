from datetime import datetime
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