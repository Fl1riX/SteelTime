from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class BanCreate(BaseModel):
    """Схема для бана пользователя"""
    reason: str
    user_id: int
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(extra="forbid")
    
class BanResponse(BanCreate):
    """Схема ответа при бане пользователя"""
    id: int
    banned_at: datetime
    
    
    model_config = ConfigDict(from_attributes=True)