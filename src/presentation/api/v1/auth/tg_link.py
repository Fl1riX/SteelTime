from datetime import datetime, timezone, timedelta
import secrets
from fastapi import Request, Depends, APIRouter
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.db.database import get_db
from src.domain.services.auth_service import AuthService
from src.domain.services.tg_link_service import TgLinkService
from src.presentation.api.v1.exceptions import NotCorrect
from src.shared.schemas.auth_schema import GenerateMagicLincShema
from src.logger import logger

router = APIRouter(prefix="/auth", tags=["Магические ссылки"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/telegram/generate-link")
@limiter.limit("3/minute")
async def create_telegram_magic_link(
    request: Request,
    telegram_id: GenerateMagicLincShema,
    db: AsyncSession = Depends(get_db)
):
    """Создание токена для привязки телеграм бота к аккаунту"""
    tg_id = telegram_id.model_dump()["telegram_id"]
    logger.debug(f"Получен tg_id: {tg_id}")
    
    if await AuthService.is_telegram_linked(tg_id, db):
        logger.warning(f"Этот аккаунт телеграм уже привязан к платформе: {tg_id}")
        raise NotCorrect("Уже привязан")
    
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    logger.info("Сохранение magic токена...")
    await TgLinkService.save_link_token(token=token, expires_at=expires, db=db, telegram_id=tg_id)
    
    return {"token": token}


    
    
    
 
















