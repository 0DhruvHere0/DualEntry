from datetime import datetime
from pydantic import BaseModel, ConfigDict
class CounterpartCreate(BaseModel):
    user_id: int
    counterpart_id: int
    relationship_type: str
class CounterpartResponse(BaseModel):
    id: int
    user_id: int
    counterpart_id: int
    counterpart_name: str
    relationship_type: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class CounterpartResponse(BaseModel):
    id: int
    user_id: int
    counterpart_id: int
    counterpart_name: str
    relationship_type: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)