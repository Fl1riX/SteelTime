import re

from pydantic.functional_validators import BeforeValidator
from typing import Annotated
from src.logger import logger

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

def validate_tg_id(value: int | str) -> str:
    if isinstance(value, int):
        value = str(value)
        
    if not value.isdigit():
        raise ValueError("Telegram Id должен содержать только цифры")
    
    if len(str(value)) < 9 or len(str(value)) > 12:
        raise ValueError("Неверная длинна id в telegram")
    
    if int(value) < 0:
        raise ValueError("id аккаунта в telegram не может быть отрицательным")
    return str(value)

TgId = Annotated[str, BeforeValidator(validate_tg_id)]

def validate_email(value: str) -> str:
    if len(value) < 5:
        raise ValueError("Email слишком короткий")
    if len(value) > 50:
        raise ValueError("Email слишком длинный")
    if len(value.split("@")) != 2:
        raise ValueError("Введен не корректный email")
    
    return value

Email = Annotated[str, BeforeValidator(validate_email)]

def validate_login(login: str) -> str:
    """Валидирует login, принимая email, телефон или telegram_id"""
    logger.info(f"Валидация логина: {login}...")
    if re.match(r"^\+[0-9]{11,16}$", login):
        return login
    if login.isdigit():
        tg_id = validate_tg_id(login)
        return str(tg_id)
    if '@' in login and re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",  login):
        email = validate_email(login)
        return email
    
    logger.warning("Login должен быть email, номером телефона (+...) или Telegram ID")
    raise ValueError("Login должен быть email, номером телефона (+...) или Telegram ID")

Login = Annotated[str, BeforeValidator(validate_login)]