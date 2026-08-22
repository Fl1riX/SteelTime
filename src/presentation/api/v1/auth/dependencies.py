from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.database import get_db
from src.presentation.api.v1.auth.jwt_handler import decode_token
from src.domain.services.user_service import UserService
from src.domain.models.user_model import User, UserRole
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
    
    logger.info(f"Проверка на наличие банов у пользователя с id: {current_user.id}")
    for ban in current_user.bans: # current_user.bans вернет список объектов(банов)
        if ban.is_active: # Проходимя по списку и если если бан активен, то возвращаем ошибку
            logger.warning(
                f"Пользователь с id: {current_user.id} "
                f"забанен по причине: {ban.reason}"
            )
            raise NoAccess(
                f"Вы были забанены.\n"
                f"Причина: {ban.reason}\n"
                f"Срок истечения: {ban.expires_at}"
            )
        
    logger.info(
        f"Пользователь с id: {current_user.id} "
        "не имеет активных банов"
    )
    
    return current_user
    
def check_user_privilege(*roles: UserRole):
    """Dependency фабрика для проверки роли пользователя"""
    
    async def check_role(
        active_user: User = Depends(get_active_user)
    ) -> User:
        logger.info(
            f"Проверка прав пользователя с id: {active_user.id}"
        )
        
        if active_user.role not in roles:
            logger.warning(
                f"Пользователь с id: {active_user.id} "
                f"не имеет ни одной из ролей: {roles}"
            )
            
            raise NoAccess("У вас нет прав для этого действия")
        
        logger.info(
            f"Пользователь с id: {active_user.id} "
            f"имеет привилегию: {roles}. Доступ разрешен"
        )
        return active_user
        
    return check_role


