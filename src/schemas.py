from pydantic import BaseModel, ConfigDict, Field, validator
from pydantic.functional_validators import BeforeValidator
from datetime import datetime
from typing import Annotated, Optional

# проверяем номер телефона
def validate_phone(value: str) -> str:
    if not value.startswith('+'):
        raise ValueError("Номер должен начинаться с +")
    if len(value) < 12:
        raise ValueError("Номер слишком короткий")
    if len(value) > 15:
        raise ValueError("Номер слишком длинный")
    return value # возвращаем валидитрованное значение

PhoneNumber = Annotated[str, BeforeValidator(validate_phone)] # создаем новый тип, где берем строку и проверяем ее перед испоьзованием

def validate_tg_id(value: int) -> int:
    if len(str(value)) < 9 or len(str(value)) > 12:
        raise ValueError("Неверная длинна id в telegram")
    if value < 0:
        raise ValueError("id аккаунта в telegram не может быть отрицательным")
    return value

TgId = Annotated[int, BeforeValidator(validate_tg_id)]

def validate_email(value: str) -> str:
    if len(value) < 5:
        raise ValueError("Email слишком короткий")
    if len(value) > 50:
        raise ValueError("Email слишком длинный")
    if len(value.split("@")) != 2:
        raise ValueError("Введен не корректный email")
    
    return value

Email = Annotated[str, BeforeValidator(validate_email)]

"""Юзер"""
class UserCreate(BaseModel):
    telegram_id: TgId
    username: str
    phone: PhoneNumber
    email: Email 
    password: str
    
    model_config = ConfigDict(extra='forbid') # запрещаем не указанные поля

class UserResponse(BaseModel):
    id: int
    telegram_id: TgId
    username: str
    phone: PhoneNumber
    email: Email 
    
    class Config:
        from_attributes = True
        
class RegisterResponse(BaseModel):
    user: UserCreate
    token: str
    token_type: str
    
    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    #id: int
    telegram_id: Optional[TgId] = None
    email: Optional[Email] = None
    phone: Optional[PhoneNumber] = None
    password: str
    
    model_config = ConfigDict(extra='forbid')
    #! TODO проавлидировать что хотябы в 1 поле естьь данные для входа
    
class UserLoginResponse(BaseModel):
    id: int
    token: str
    token_type: str
    
    class Config:
        from_attributes = True

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
        
"""Услуга"""
class ServiceCreate(BaseModel):
    name: str
    price: int
    description: str
    duration: str
    address: str
    entrepreneur_id: int
    
    model_config = ConfigDict(extra='forbid')

class ServiceResponse(ServiceCreate):
    id: int
    
    class Config:
        from_attributes = True

"""Запись"""
class AppointmentCreate(BaseModel):
    date: datetime
    comment: str
    service_id: int
    entrepreneur_id: int
    user_id: int
    
    model_config = ConfigDict(extra='forbid')

class AppointmentResponse(AppointmentCreate):
    id: int
    
    class Config:
        from_attributes = True

        