from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional
from datetime import datetime

from .types import TgId, Email, PhoneNumber, Login
from .user_schema import UserPublic

class TgLinkSchema(BaseModel):
    """Схема для привязки телеграм бота к профилю"""
    telegram_id: TgId
    token: str
    expires_at: datetime
    
    model_config = ConfigDict(extra='forbid')
    
class UserLogin(BaseModel):
    login: Login = Field(max_length=50, min_length=10)
    password: str = Field(max_length=255, min_length=8)
    
    model_config = ConfigDict(extra='forbid')
    
class ChangePassword(BaseModel):
    login: Login = Field(max_length=50, min_length=10)
    new_password: str = Field(max_length=255, min_length=8)
    current_password: str = Field(max_length=255, min_length=8)
    
    model_config = ConfigDict(extra='forbid')
    
class UserLoginResponse(BaseModel):
    id: int
    access_token: str
    token_type: str
    
    class Config:
        from_attributes = True
        
class UserRegisterResponse(BaseModel):
    user: UserPublic
    token: str
    token_type: str
    
    class Config:
        from_attributes = True

class UserRegister(BaseModel):
    telegram_id: Optional[TgId] = None 
    username: str = Field(max_length=50)
    phone: PhoneNumber | None
    email: Email 
    password: str = Field(max_length=255, min_length=8)
    is_entrepreneur: Optional[bool] = False
    full_name: Optional[str] = None
    
    model_config = ConfigDict(extra='forbid') # запрещаем не указанные поля
    
    @model_validator(mode="after")
    def validate_entrepreneur_name(self):
        if self.is_entrepreneur and not self.full_name:
            raise ValueError("Предприниматель обязан заполнить поле с именем")
        return self