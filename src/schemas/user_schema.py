from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional
from .types import TgId, Email, PhoneNumber, Login
from datetime import datetime

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

class UserPublic(BaseModel):
    telegram_id: TgId | None 
    username: str = Field(max_length=50)
    phone: PhoneNumber | None
    email: Email 
    
    model_config = ConfigDict(extra='forbid')
    
class UserRegisterResponse(BaseModel):
    user: UserPublic
    token: str
    token_type: str
    
    class Config:
        from_attributes = True
        
class UserUpdate(BaseModel):
    telegram_id: Optional[TgId] = None
    username: Optional[str] = None
    phone: Optional[PhoneNumber] = None
    email: Optional[Email] = None
    
    model_config = ConfigDict(extra='forbid') # запрещаем не указанные поля
    
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