from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .types import PhoneNumber, Email, TgId

class EntrepreneurCreate(BaseModel):
    full_name: str
    phone: PhoneNumber
    password: str
    telegram_id: TgId
    email: Email
    
    model_config = ConfigDict(extra='forbid')
    
class EntrepreneurResponse(BaseModel):
    id: int
    full_name: str
    phone: PhoneNumber
    telegram_id: TgId
    email: Email
    created_at: datetime
    
    class Config:
        from_attributes = True