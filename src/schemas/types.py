from pydantic.functional_validators import BeforeValidator
from typing import Annotated

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