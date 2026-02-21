from src.shared.schemas import user_schema, auth_schema
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.db.models import User
from src.logger import logger

class UserService:
    @classmethod
    async def check_user_exists(cls, user: auth_schema.UserLogin | auth_schema.ChangePassword, db: AsyncSession):
        """Проверка существования пользователя при входе в аккаунт"""
        result = await db.execute(select(User).where(
            or_(
                    User.email == user.login,
                    User.phone == user.login
                )   
            )
        )
        existing = result.scalars().first()
        return existing
    
    @staticmethod
    async def create_user(user: dict, db: AsyncSession):
        """Создание нового пользователя"""
        new_user = User(**user)
        try:
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            logger.info("POST: Данные нового пользователя успешно записанны ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"POST: ❌ Ошибка ❌: {e}")
            raise
        
        return new_user
    
    @staticmethod
    async def find_user_by_id(id: int, db: AsyncSession):
        """Поиск пользователя по id"""
        result = await db.execute(select(User).where(
            User.id == id
        )) 
        user = result.scalars().first() 
        
        return user
    
    @staticmethod
    async def delete_user(db: AsyncSession, user: User):
        """Удаление пользователя"""
        try:
            await db.delete(user)
            await db.commit()

            logger.info("DELETE: Данные успешно удалены ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"DELETE: ❌ Ошибка ❌: {e}")
            raise
            
    @staticmethod
    async def update_user(new_user: user_schema.UserUpdate, db: AsyncSession, user: User):
        """Обновление данных пользователя"""
        # построчно передираем словарь
        for key, value in new_user.model_dump().items(): # items построчно разбивает словрь на пары (ключ, значение)
            if hasattr(user, key) and value is not None: # если в user(в бд) есть такое поле
                setattr(user, key, value)                # то задаем значение для поля 

        try:
            await db.commit()
            await db.refresh(user)

            logger.info("PUT: Данные пользователя успешно обновлены ✅")
            return user
        except Exception as e:
            await db.rollback()
            logger.error(f"PUT: ❌ Ошибка ❌: {e}")
            raise
    
    
        
    