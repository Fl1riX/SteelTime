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
    async def link_account(db: AsyncSession, link_token: MagicTokens, user: User):
        """
        Привязываем телеграм бота к аккаунту
            db: AsyncSession
            link_token: MagicTokens
            user: User
        -> Nothing
        """
        if link_token.used:
            logger.warning(f"Токен уже ииспользован: {link_token}")
            raise ValueError("Токен уже ииспользован")
        
        if user.telegram_id is not None:
            logger.warning(f"У пользоватьеля: {user.id} уже привязан TG: {user.telegram_id}")
            raise ValueError("Telegram уже привязан")
        
        if link_token.expires_at <= datetime.now(timezone.utc):
            logger.info(f"Токен: {link_token} просрочен")
            raise ValueError("Токен просрочен")
        
        user.telegram_id = link_token.telegram_id

        link_token.used = True
        link_token.telegram_linked_at = datetime.now(timezone.utc)
        await db.commit()
        
        logger.info(f"Привязка удалась: user={user.id}, tg={link_token.telegram_id}")
    
    @staticmethod
    async def find_token(token: str, db: AsyncSession) -> bool:
        """
        Ищет токен в базе данных
            token: str
            db: AsyncSession
        -> bool
        """
        logger.info("Поиск токен в базе данных")
        result = await db.execute(select(MagicTokens).where(
            MagicTokens.token == token
        ))
        token = result.scalars().first()
        if not token:
            logger.info("Токен не найден в базе данных")
            return False
        
        logger.info(f"Найден токен: {token}")
        return True