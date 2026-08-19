from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.database import get_db
from src.presentation.api.v1.auth.jwt_handler import decode_token
from src.domain.services.user_service import UserService
from src.domain.models.user_model import User
from src.presentation.api.v1.exceptions import NoAccess, Unauthorized, NotFound
from src.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") # указываем URL эндпоинта логина

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Возвращаем id пользователя, 
    который пытается получить доступ к защищенной ручке, 
    т.е достаем его из заголовков
    """
    logger.info(f"🔍 Получен токен: {token}...")
    payload = decode_token(token)
    logger.info(f"Декодированный токен: {payload}")

    if not payload:
        logger.warning("Невалидный или истекший токен")
        raise Unauthorized(
            message="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")

    if not user_id:
        logger.warning("В токене отсутствует user_id")
        raise Unauthorized(
            message="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_id

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """Возвращает User из бд"""
    payload = decode_token(token)
    
    if not payload:
        logger.warning("Невалидный или истекший токен")
        raise Unauthorized(
            message="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    
    if not user_id:
        logger.warning("Токен не содержит user_id")
        raise Unauthorized(
            message="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = await UserService.find_user_by_id(id=user_id, db=db)
    
    if not user:
        logger.warning(f"Пользователь с id: {user_id} не найден")
        raise NotFound(
            message="Пользователь не найден"
        )
    
    return user
        
async def get_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяем что пользователь не забанен 
    и возвращаем объект пользователя, 
    если он не забанен или ошибку 403
    """
    
    for ban in current_user.bans: # current_user.bans вернет список объектов(банов)
        if ban.is_active: # Проходимя по списку и если если бан активен, то возвращаем ошибку
            raise NoAccess(
                f"Вы были забанены.\n \
                Причина: {ban.reason}\n \
                Срок истечения: {ban.expires_at}"
            )
        
    return current_user
    
    
    
    


