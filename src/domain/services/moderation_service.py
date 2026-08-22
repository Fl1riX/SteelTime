from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timezone

from src.shared.schemas.moderation_schema import BanCreate
from src.logger import logger
from src.domain.models.ban_model import Ban
from src.domain.services.exceptions import UserAlreadyBanned, BanPrivilegeError, UserNotFound
from src.domain.services.user_service import UserService
from src.domain.models.user_model import UserRole

class ModerationService:
    @classmethod
    async def ban_user(
        cls,
        ban_info: BanCreate,
        banned_by: int,
        db: AsyncSession
    ) -> Ban:
        logger.info("Проверка на возможность бана этого пользователя...")
        
        ban_possibly = await cls.is_ban_possible(banned_by, ban_info.user_id, db)
        if not ban_possibly:
            raise BanPrivilegeError()
        
        logger.info(f"Проверка наличия банов у пользователя: {ban_info.user_id}...")
        user_banned = await cls.is_user_banned(ban_info.user_id, db)
        if user_banned:
            raise UserAlreadyBanned()
        
        logger.info("Запись бана в базу данных...")
        new_ban = Ban(
            **ban_info.model_dump(),
            banned_by=banned_by
        )
        
        try:
            db.add(new_ban)
            await db.commit()
            await db.refresh(new_ban)
            logger.info("Бан успешно добавлен!")
            
            return new_ban
        except Exception as e:
            await db.rollback()
            logger.error(f"Ошибка при создании бана: {e}")
            raise
        
    @classmethod
    async def is_user_banned(
        cls,
        user_id: int,
        db: AsyncSession
    ) -> bool:
        logger.info(f"Проверка наличия банов у пользователя: {user_id}...")
        result = await db.execute(select(Ban).where(
                Ban.user_id == user_id,
                Ban.revoked_at.is_(None),
                or_ (
                    Ban.expires_at.is_(None),
                    Ban.expires_at > datetime.now(timezone.utc)
                ) 
            )
        )
        ban_exists = result.scalars().one_or_none()
        
        if not ban_exists:
            logger.info(f"У пользователя с id: {user_id} нет активных банов")
            return False
        
        logger.info(f"Пользователь с id: {user_id} забанен")
        return True
        
    @classmethod
    async def is_ban_possible(
        cls,
        moder_id: int,
        user_id: int, 
        db: AsyncSession
    ) -> bool:
        logger.info("Проверка существования пользвателей в базе данных...")
        moder = await UserService.find_user_by_id(moder_id, db)
        if not moder:
            logger.info(f"Пользователь {moder_id} не существует")
            raise UserNotFound()
        
        user = await UserService.find_user_by_id(user_id, db)
        if not user:
            logger.info(f"Пользователь {user_id} не существует")
            raise UserNotFound()
        
        if moder.role == user.role:
            return False
        
        if moder.role == UserRole.ADMIN:
            return True
        
        if user.role == UserRole.ADMIN:
            return False
        
        return True