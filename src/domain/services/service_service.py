from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.schemas import service_schema
from src.infrastructure.db.models import Service
from src.logger import logger
from src.domain.services.user_service import UserService

class ServiceService:
    @staticmethod 
    async def is_name_indicated(user_id:int, db: AsyncSession) -> bool:
        """
        Проверка, что у предпринимателя указано полное имя
            user_id:int
            db: AsyncSession
        -> bool
        """
        logger.info(f"Проверка что у пользователя: {user_id} задано ФИО...")
        user = await UserService.find_user_by_id(user_id, db)

        if user and user.full_name:
            logger.info("Пользователь указал ФИО ✅")
            return True
        logger.info("Пользователь не указал ФИО")
        return False
    
    @staticmethod
    async def set_fullname(user_id: int, fullname: str, db: AsyncSession) -> bool:
        """
        Задает полное имя пользователя
            user_id: int
            fullname: str
            db: AsyncSession
        -> bool
        """
        logger.info(f"Ищем пользователя {user_id} в БД...")
        user = await UserService.find_user_by_id(user_id, db)
        if user is not None:
            logger.info("Найден пользователь. Запись ФИО...")
            user.full_name = fullname
            await db.commit()
            return True
        logger.info("Пользователь не найден")
        return False
        
    @staticmethod
    async def find_service_by_id(id: int, db: AsyncSession):
        """Поиск улуги по id"""
        result = await db.execute(select(Service).where(
            Service.id == id
        ))
        service = result.scalars().first()
        
        return service
    
    @staticmethod
    async def find_by_name(
        name: str, 
        address: str,
        current_user_id: int, 
        db: AsyncSession
    ) -> Service | None:
        """Ищет услугу по имени, адресу и id предпринимателя """
        result = await db.execute(select(Service).where(
            and_(
                Service.name == name,
                Service.address == address,
                Service.entrepreneur_id == current_user_id
            )
        ))
        existing = result.scalars().first()
        
        return existing

    @staticmethod
    async def create_service(service: service_schema.ServiceCreate, current_user_id: int, db: AsyncSession):
        """Создает новую услугу"""
        user = await UserService.find_user_by_id(current_user_id, db=db)
        if not user:
            logger.info(f"Пользователь с id: {current_user_id} не найден")
            raise ValueError(f"Пользователь с id: {current_user_id} не найден")
        
        if not user.full_name:
            raise ValueError("У пользователя не указано полное имя")
        
        if not user.is_entrepreneur:
            user.is_entrepreneur = True
            await db.flush() # сохранение изменения флага 
        
        service_data = service.dict(exclude={"fullname"})
        new_service = Service(**service_data, entrepreneur_id=current_user_id)
    
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
        """Удаляет услугу"""     
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
    async def update_service(db: AsyncSession, new_service: service_schema.ServiceCreate, service: Service):
        """Обновляет данные об услуге"""
        for key, value in new_service.model_dump().items():
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