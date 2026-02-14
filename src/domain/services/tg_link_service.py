from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.domain.db.models import User,  MagicTokens
from src.logger import logger

class TgLinkService:
    @staticmethod
    async def check_telegram_connection(tg_id: str, db: AsyncSession) -> User | None:
        result = await db.execute(select(User).where(
            User.telegram_id == tg_id
        ))
        user_info = result.scalar()
        if user_info is None:
            logger.info(f"Пользователь с id: {tg_id} не привязал бота")
            return user_info
        return user_info
    
    @staticmethod
    async def save_link_token(expires_at: datetime, telegram_id: int, token: str, db: AsyncSession):
        """Сохранение magic токенов в таблицу"""
        link_token = MagicTokens(
            telegram_id=telegram_id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(link_token)
        await db.commit()
        logger.info(f"Сохранен link токен: tg_id={link_token.telegram_id}")
    
    @staticmethod
    async def check_magic_token(token: str, db: AsyncSession):
        """Проверка существования magic токена в бд"""
        result = await db.execute(select(MagicTokens).where(
            MagicTokens.token == token,
            MagicTokens.expires_at > datetime.now(timezone.utc),
            MagicTokens.used == False
        ))
        link_token = result.scalar_one_or_none()
        return link_token
            
    @staticmethod
    async def link_account(db: AsyncSession, link_token, user):
        """Привязываем телеграм бота к аккаунту"""
        if link_token.telegram_id != user.telegram_id:
            user.telegram_id = link_token.telegram_id

        link_token.used = True
        await db.commit()
        
        logger.info(f"Привязка удалась: user={user.id}, tg={link_token.telegram_id}")
        
    #@staticmethod
    #async def make_token_used(db: AsyncSession, token: str):
    #    """Меняем значение токена на использованное"""
    #    logger.info(f"Пометка токена: {token} как использованного...")
    #    result = await db.execute(select(MagicTokens).where(
    #        MagicTokens.token == token
    #    ))
    #    entry = result.scalars().first()
    #    if not entry:
    #        logger.warning(f"Токен: {token} не найден в таблице MagicTokens")
    #        raise ValueError(f"Токен: {token} не найден в таблице MagicTokens")
    #    if entry.used:
    #        return
    #    entry.used = True
    #    
    #    db.add(entry)
    #    await db.commit()