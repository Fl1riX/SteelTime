from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from logger import logger
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# настройка хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

def hash_password(password: str) -> str:
    """Хэшируем пароль"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяем  пароль"""
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict) -> str:
    """Создаем JWT токен"""
    to_encode = data.copy() # копируем данные, чтобы не менять исходный словарь
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # через сколько токен становится не действительным 
    to_encode.update({"exp": expire}) # добавляем чремя через которе истечет действие токена
    to_encode.update({"iat": datetime.utcnow()}) # когда выдан
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # кодируем данные в токен
    logger.info(f"JWT токен создан для user_id={data.get('sub')}")
    return encoded_jwt

def decode_token(token: str) -> dict | None:
    """Декодировать JWT токен"""
    try:
        payload = jwt.decode(token, 
                             SECRET_KEY, 
                             algorithms=[ALGORITHM], 
                             options={
                                 "require_exp": True,      # проверяем сровк действия токена
                                 "verify_signature": True  # проверяем подпись
                             }
                            ) # декодируем токен
        sub_value = payload.get("sub") # извлекаем данные о пользователе "sub" = subject
        
        if sub_value is None or isinstance(sub_value, int):
            logger.error("Неверный субъект")
            return None
        
        user_id: int = sub_value
        
        # проверяем что пользователь существует
        if user_id is None:
            logger.warning("Токен без user_id")
            return None
        
        return {"user_id": user_id}
    except JWTError:
        logger.warning("Невалидный токен")
        return None