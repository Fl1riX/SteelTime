import secrets

from datetime import datetime, timezone, timedelta
from fastapi import Request, Depends, APIRouter
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.database import get_db
from src.domain.services.tg_link_service import TgLinkService
from src.presentation.api.v1.exceptions import NotCorrect, NoAccess
from src.logger import logger

router = APIRouter(prefix="/auth", tags=["Магические ссылки"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/telegram/generate-link/{telegram_id}")
@limiter.limit("3/minute")
async def create_telegram_magic_link(
    request: Request,
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Создание токена для привязки телеграм бота к аккаунту
        telegram_id: int
        db: AsyncSession
    -> dict
    """
    logger.debug(f"Получен запрос на привязку аккаунта к боту tg_id: {telegram_id}")
    
    logger.info("Проверка заголовка X-Bot-Secret...")
    bot_secret_header = request.headers.get("X-Bot-Secret")
    
    if not bot_secret_header:
        logger.info("В заголовке отсутствует секретный ключ")
        raise NoAccess("Недостаточно прав для доступа к этому ресурсу")
    
    logger.info("Сравнение ключей...")
    verify_key = TgLinkService.verify_bot_secret_key(bot_secret_header)

    if not verify_key:
        logger.info("Предоставленный ключ не совпадает с секретным ключом")
        raise NoAccess("Недостаточно прав для доступа к этому ресурсу")
    
    logger.info("Проверка наличия привязки аккаунта к платформе...")
    if await TgLinkService.check_telegram_connection(telegram_id, db):
        logger.warning(f"Этот аккаунт телеграм уже привязан к платформе: {telegram_id}")
        raise NotCorrect("Этот аккаунт телеграм уже привязан к платформе")
    
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    #! TODO: Добавить изоляцию на уровне docker
    
    logger.info("Сохранение magic токена...")
    await TgLinkService.save_link_token(token=token, expires_at=expires, db=db, telegram_id=telegram_id)
    logger.info("Токен успешно сохранен!")
    
    return {"token": token}


    
    
    
 
















