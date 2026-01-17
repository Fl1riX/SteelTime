from pydantic import BaseModel, ConfigDict
from typing import Optional
from .types import TgId, Email, PhoneNumber

class UserRegister(BaseModel):
    telegram_id: TgId
    username: str
    phone: PhoneNumber
    email: Email 
    password: str
    
    model_config = ConfigDict(extra='forbid') # запрещаем не указанные поля

class UserRegisterResponse(BaseModel):
    user: UserRegister
    token: str
    token_type: str
    
    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    telegram_id: Optional[TgId] = None
    email: Optional[Email] = None
    phone: Optional[PhoneNumber] = None
    password: str
    
    model_config = ConfigDict(extra='forbid')
    #! TODO проавлидировать что хотябы в 1 поле есть данные для входа
    
class UserLoginResponse(BaseModel):
    id: int
    token: str
    token_type: str
    
    class Config:
        from_attributes = True
        
class UserResponse(BaseModel):
    id: int
    telegram_id: TgId
    username: str
    phone: PhoneNumber
    email: Email 
    
    class Config:
        from_attributes = True