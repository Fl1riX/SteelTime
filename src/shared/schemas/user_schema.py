from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from .types import TgId, Email, PhoneNumber
from datetime import datetime

class UserPublic(BaseModel):
    telegram_id: Optional[TgId] = None 
    username: str = Field(max_length=50)
    phone: PhoneNumber 
    email: Email 
    fullname: Optional[str] = None
    
    model_config = ConfigDict(extra='forbid')
        
class UserUpdate(BaseModel):
    telegram_id: Optional[TgId] = None
    username: Optional[str] = None
    phone: Optional[PhoneNumber] = None
    email: Optional[Email] = None
    
    model_config = ConfigDict(extra='forbid') # запрещаем не указанные поля
        
class UserResponse(BaseModel):
    id: int
    telegram_id: TgId | None
    username: str
    phone: PhoneNumber | None
    email: Email 
    created_at: datetime
    is_entrepreneur: bool
    full_name: str | None
    
    class Config:
        from_attributes = True
        
