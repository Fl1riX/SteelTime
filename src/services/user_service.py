from src import schemas
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import User
from src.logger import logger

class UserService:
    @staticmethod
    async def check_user_exists(user: schemas.UserCreate | schemas.UserLogin, db: AsyncSession):
        """Проверяем существование польщователя по id в telegram, email или номеру телефона"""
        result = await db.execute(select(User).where(
            or_(
                User.telegram_id == user.telegram_id,
                User.email == user.email,
                User.phone == user.phone
                )
            )
        )
        existing = result.scalars().first()
        return existing
    
    @staticmethod
    async def create_user(user: dict, db: AsyncSession):
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
        result = await db.execute(select(User).where(
            User.id == id
        )) 
        user = result.scalars().first() 
        
        return user
    
    @staticmethod
    async def delte_user(db: AsyncSession, user: User):
        try:
            await db.delete(user)
            await db.commit()

            logger.info("DELETE: Данные успешно удалены ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"DELETE: ❌ Ошибка ❌: {e}")
            raise
            
    @staticmethod
    async def update_user(new_user: schemas.UserCreate, db: AsyncSession, user: User):
        # построчно передираем словарь
        for key, value in new_user.dict().items(): # items построчно разбивает словрь на пары (ключ, значение)
            if hasattr(user, key) and value is not None: # если в user(в бд) есть такое поле
                setattr(user, key, value)                # то задаем значение для поля 

        try:
            await db.commit()
            await db.refresh(user)

            logger.info("PUT: Данные пользователя успешно обновлены ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"PUT: ❌ Ошибка ❌: {e}")
            raise