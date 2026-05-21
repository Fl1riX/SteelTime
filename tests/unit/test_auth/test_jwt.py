
from src.presentation.api.v1.auth.jwt_handler import (
    hash_password, verify_password,
    create_access_token
)

def test_hash_password(): 
    """Тестирование хэширования паролей"""
    password = "password_123"
    wrong_password = "password"
    
    wrong_hash = hash_password(wrong_password)
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    assert verify_password(password, hash1) is True, "Пароли не совпадают"
    assert verify_password(password, hash2) is True, "Пароли не совпадают"
    
    assert verify_password(wrong_hash, hash1) is False, "Верный и не верный пароли совпадают"
    assert verify_password(wrong_hash, hash2) is False, "Верный и не верный пароли совпадают"

def test_create_access_token():
    """Тестирование создания JWT токена"""
    
    data = {"sub": 1234}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 100, "Токен слишком длинный"
    
def test_decode_token():
    """Тестирование расшифровки токена"""
    
    