from pydantic import BaseModel, ConfigDict, Field, validator
from pydantic.functional_validators import BeforeValidator
from datetime import datetime
from typing import Annotated

#! TODO: переделать валидацию под изменившиеся поля в бд

# проверяем номер телефона
def validate_phone(value: str) -> str:
        if not value.startswith('+'):
            raise ValueError("Номер должен начинаться с +")
        if len(value) < 12:
            raise ValueError("Номер слишком короткий")
        return value # возвращаем валидитрованное значение

PhoneNumber = Annotated[str, BeforeValidator(validate_phone)] # создаем новый тип, где берем строку и проверяем ее перед испоьзованием

def validate_tg_id(value: int) -> int:
    if len(str(value)) < 9 or len(str(value)) > 12:
        raise ValueError("Неверная длинна id в telegram")
    if value < 0:
        raise ValueError("id аккаунта в telegram не может быть отрицательным")
    return value

TgId = Annotated[int, BeforeValidator(validate_tg_id)]

"""Юзер"""
class UserCreate(BaseModel):
    telegram_id: TgId
    username: str
    phone: PhoneNumber
    created_at: datetime
    
    model_config = ConfigDict(extra='forbid') # запрещаем не указанные поля

class UserResponse(UserCreate):
    id: int
    
    class Config:
        from_attributes = True
        
"""Услуга"""
class ServiceCreate(BaseModel):
    name: str
    price: int
    description: str
    price_type: str
    duration: int
    entrepreneur_id: int
    
    model_config = ConfigDict(extra='forbid')

class ServiceResponse(ServiceCreate):
    id: int
    
    class Config:
        from_attributes = True

"""Запись"""
class AppointmentCreate(BaseModel):
    date: datetime
    user_id: int
    comment: str
    address: str
    service_id: int
    entrepreneur_id: int
    user_id: int
    
    model_config = ConfigDict(extra='forbid')

class AppointmentResponse(AppointmentCreate):
    id: int
    
    class Config:
        from_attributes = True
        
class EntrepreneurCreate(BaseModel):
    full_name: str
    phone: PhoneNumber
    telegram_id: TgId

class EntrepreneurResponse(EntrepreneurCreate):
    id: int
    
    class Config:
        from_attributes = True
    
        