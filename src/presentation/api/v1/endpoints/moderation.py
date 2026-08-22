from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger
from src.infrastructure.db.database import get_db
from src.presentation.api.v1.auth.dependencies import check_user_privilege
from src.domain.models.user_model import UserRole
from src.limiter import limiter
from src.shared.schemas.moderation_schema import BanCreate, BanResponse
from src.domain.services.user_service import UserService
from src.presentation.api.v1.exceptions import NotFound, ConflictError
from src.domain.services.moderation_service import ModerationService
from src.domain.services.exceptions import UserAlreadyBanned

router = APIRouter(tags=["Модерация"], prefix="/moderation")

@router.post("/ban")
@limiter.limit("5/minute")
async def ban_user(
    request: Request,
    ban_info: BanCreate,
    moder_info = Depends(check_user_privilege(UserRole.MODERATOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> BanResponse:
    logger.info("POST: Проверка существования пользователя...")
    
    user_exists = await UserService.find_user_by_id(
        ban_info.user_id,
        db
    )
    
    if not user_exists:
        logger.info(f"POST: ❌ Пользователь с id: {ban_info.user_id} не найден ❌")
        raise NotFound("Пользователь не найден")
    
    logger.info(f"POST: Добавление бана пользователю: {ban_info.user_id}")
    
    try:
        ban = await ModerationService.ban_user(
            ban_info,
            moder_info,
            db
        )
    except UserAlreadyBanned:
        raise ConflictError(f"У пользователя {ban_info.user_id} уже есть активный бан")
    
    return ban