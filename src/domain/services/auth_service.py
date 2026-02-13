from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.schemas import auth_schema
from src.domain.db.models import User
from src.logger import logger
from src.presentation.api.v1.auth.jwt_handler import hash_password
from src.domain.services.exceptions import UserNotFound
from src.domain.services.user_service import UserService

class AuthService:
    @staticmethod
    async def is_telegram_linked(telegram_id: int, db: AsyncSession) -> bool:
        """Проверка привязки телеграм бота к аккаунту пользователя"""
        logger.info("Проверка привязки бота к аккаунту...")
        result = await db.execute(select(User).where(
            User.telegram_id == telegram_id
        ))
        linked = result.scalars().first()
        if not linked or not linked.telegram_id:
            logger.info("Бот не привязан к аккаунту!")
            return False
        logger.info("Бот привязан к аккаунту")
        return True
    
    @classmethod
    async def update_user_password(cls, user_data: auth_schema.ChangePassword, db: AsyncSession):
        """Обновление пароля пользователя"""
        user = await UserService.check_user_exists(user=user_data, db=db)
        if not user:
            logger.warning(f"Пользователь не зарегистрирован: {user_data.login}")
            raise UserNotFound
        user.password = hash_password(user_data.new_password)
        await db.commit()

    @staticmethod
    async def find_user_registration(user: auth_schema.UserRegister, db: AsyncSession):
        """Проверяем существование пользователя по id в telegram, email или номеру телефона"""
        result = await db.execute(select(User).where(
            or_(
                User.telegram_id == user.telegram_id,
                User.email == user.email,
                User.phone == user.phone
                )
            )
        )
        registred = result.scalars().first()
        return registred
    
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
    
    
        