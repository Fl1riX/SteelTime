import schemas

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Service
from logger import logger

class ServiceService:
    @staticmethod
    async def find_service_by_id(id: int, db: AsyncSession):
        result = await db.execute(select(Service).where(
            Service.id == id
        ))
        service = result.scalars().first()
        
        return service
    
    @staticmethod
    async def find_by_name(service: schemas.ServiceCreate, db: AsyncSession):
        result = await db.execute(select(Service).where(
            and_(
                Service.name == service.name,
                Service.entrepreneur_id == service.entrepreneur_id
            )
        ))
        existing = result.scalars().first()
        
        return existing

    @staticmethod
    async def create_service(service: schemas.ServiceCreate, db: AsyncSession):
        new_service = Service(**service.dict())
    
        try:
            db.add(new_service)
            await db.commit()
            await db.refresh(new_service)

            logger.info("POST: Данные об услуге успешно записанны в бд ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Ошибка ❌: {e}")
            raise
            
        return new_service
    
    @staticmethod
    async def delete_service(service: Service, db: AsyncSession):
        logger.info("DELETE: Услуга найдена ✅. Удаление...")
        try:
            await db.delete(service)
            await db.commit()

            logger.info("DELETE: Улуга успешно удалена ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"DELETE: ❌ Ошибка ❌: {e}")
            raise
    
    @staticmethod 
    async def update_service(db: AsyncSession, new_service: schemas.ServiceCreate, service: Service):
        for key, value in new_service.dict().items():
            if hasattr(service, key) and value is not None:
                setattr(service, key, value)

        try:
            await db.commit()
            await db.refresh(service)

            logger.info("PUT: Данные успешно обновлены ✅")
        except Exception as e:
            await db.rollback()
            logger.error(f"PUT: ❌ Ошибка ❌: {e}")
            raise