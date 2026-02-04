from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import appointment_schema
from src.db.models import Appointment
from src.logger import logger

class AppointmentService:
    @staticmethod
    async def get_appointment_by_id(db: AsyncSession, appointment_id: int):
        result = await db.execute(select(Appointment).where(
            Appointment.id == appointment_id
        ))
        appointment = result.scalars().first()
        
        return appointment
    
    @staticmethod 
    async def find_appointment(appointment: appointment_schema.AppointmentCreate, db: AsyncSession, current_user_id: int):
        result = await db.execute(select(Appointment).where(
                and_(
                    Appointment.date == appointment.date,
                    Appointment.service_id == appointment.service_id,
                    Appointment.entrepreneur_id == appointment.entrepreneur_id,
                    Appointment.user_id == current_user_id
                )
            )
        )

        existing = result.scalars().first()
        
        return existing
    
    @staticmethod
    async def create_appointment(appointment:appointment_schema.AppointmentCreate, current_user_id: int, db: AsyncSession): 
        logger.info("POST: Запись не найдена в бд ✅. Добавление информации...")
        
        new_appointment = Appointment(**appointment.dict(), user_id=current_user_id)

        try:
            db.add(new_appointment)
            await db.commit()
            await db.refresh(new_appointment)
        except Exception as e:
            logger.error(f"❌ Ошибка ❌: {e}")
            await db.rollback()
            raise
            
        return new_appointment
    
    @staticmethod 
    async def update_appointment(db: AsyncSession, appointment_id: int, new_appointment: appointment_schema.AppointmentCreate, appointment: Appointment):
        logger.info(f"PUT: Запись с id: {appointment_id} успешно найдена в бд ✅. Обновление данных...")
        for key, value in new_appointment.model_dump().items():
            if hasattr(appointment, key) and value is not None:
                setattr(appointment, key, value)

        try:
            await db.commit()
            await db.refresh(appointment)
            logger.info("PUT: данные успешно обновлены ✅")
        except Exception as e:
            logger.error(f"❌ Ошибка ❌: {e}")
            await db.rollback()
            raise
        
    @staticmethod
    async def delete_appointment(db: AsyncSession, appointment: Appointment, appointment_id: int):
        logger.info(f"DELETE: Запись с id: {appointment_id} успешно найдена в бд ✅. Удаление данных...")
        try:
            await db.delete(appointment)
            await db.commit()
            logger.info("Данные успешно удалены из бд ✅")
        except Exception as e:
            logger.error(f"❌ Ошибка ❌: {e}")
            await db.rollback()
            raise
        