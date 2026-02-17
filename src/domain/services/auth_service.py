from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.schemas import auth_schema
from src.infrastructure.db.models import User
from src.logger import logger
from src.presentation.api.v1.auth.jwt_handler import hash_password
from src.domain.services.exceptions import UserNotFound
from src.domain.services.user_service import UserService

class AuthService:
    @classmethod
    async def update_user_password(cls, user_data: auth_schema.ChangePassword, db: AsyncSession):
        """
        Обновление пароля пользователя
            user_data: auth_schema.ChangePassword
            db: AsyncSession
        -> Null
        """
        user = await UserService.check_user_exists(user=user_data, db=db)
        if not user:
            logger.warning(f"Пользователь не зарегистрирован: {user_data.login}")
            raise UserNotFound
        user.password = hash_password(user_data.new_password)
        await db.commit()

    @staticmethod
    async def find_user_registration(user: auth_schema.UserRegister, db: AsyncSession) -> User | None:
        """
        Проверяем существование пользователя по id в telegram, email или номеру телефона
            user: auth_schema.UserRegister
            db: AsyncSession
        -> User | None
        """
        conditions  = []
        
        conditions.append(User.email == user.email)
        conditions.append(User.phone == user.phone)
        if user.telegram_id is not None:
            conditions.append(User.telegram_id == user.telegram_id)
            
        result = await db.execute(select(User).where(
            or_(*conditions)
            )
        )
        registred = result.scalars().first()
        return registred
    
    
    
        