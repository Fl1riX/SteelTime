from src import schemas
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Entrepreneur
from src.logger import logger

class EntrepreneurService:
    @staticmethod
    async def get_entrepreneur_by_id(db: AsyncSession, user_id: int):
        result = await db.execute(select(Entrepreneur).where(
            Entrepreneur.id == user_id # type: ignore
        ))
        entrepreneur = result.scalars().first()
        
        return entrepreneur
    
    @staticmethod 
    async def find_entrepreneur(db: AsyncSession, enterpreneur: schemas.EntrepreneurCreate):
        result = await db.execute(select(Entrepreneur).where(
            or_(
                Entrepreneur.telegram_id == enterpreneur.telegram_id,
                Entrepreneur.phone == enterpreneur.phone,
                Entrepreneur.email == enterpreneur.email
            )
        ))
        existing = result.scalars().first()
        
        return existing
    
    @staticmethod 
    async def create_entrepreneur(db: AsyncSession, new_entrepreneur: Entrepreneur):
        
    
        logger.info("POST: Пользователь не найден ✅. Запись в бд...")
        try:
            db.add(new_entrepreneur)
            await db.commit()
            await db.refresh(new_entrepreneur)
            logger.info("POST: Пользователь записан в бд ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"POST: ❌ Ошибка ❌: {e}")
            raise
        
    @staticmethod
    async def update_entrepreneur(db: AsyncSession, entrepreneur_id: int, new_entrepreneur: schemas.EntrepreneurCreate):
        logger.info(f"PUT: Пользователь с id: {entrepreneur_id} найден✅. Обновление данных...")
        try:
            await db.commit()
            await db.refresh(new_entrepreneur)

            logger.info("PUT: Данные обновлены ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"PUT: ❌ Ошибка ❌: {e}")
            raise
            
    @staticmethod
    async def delete_entrepreneur(db: AsyncSession, entrepreneur: Entrepreneur):
        logger.info("DELETE: Пользователь найден в бд ✅. Удаление данных...")
        try:
            await db.delete(entrepreneur)
            await db.commit()

            logger.info("DELETE: Пользователь успешно удален ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"DELETE: ❌ Ошибка ❌: {e}")
            raise