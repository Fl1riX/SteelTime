from src import schemas
from src.logger import logger
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from src.services.appointments_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["Записи"])

@router.get("/{appointment_id}", response_model=schemas.AppointmentResponse)
async def get_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"Поступил запрос: GET /appointments/{appointment_id}")
    logger.info(f"GET: Поиск записи с id: {appointment_id} в базе данных...")
    
    appointment = await AppointmentService.get_appointment_by_id(db=db, appointment_id=appointment_id)
    
    if not appointment:
        logger.error(f"GET: ❌ Запись с id: {appointment_id} не найдена в бд ❌")
        raise HTTPException(status_code=404, detail="Запись не найдена")

    logger.info(f"GET: Запись с id: {appointment_id} успешно найдена в бд ✅")

    return appointment

@router.post("/", response_model=schemas.AppointmentResponse)
async def create_appointment(appointment: schemas.AppointmentCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Поступил запрос: POST /appointments/")
    logger.info(f"POST: Проверка наличия записи в бд...")
    
    existing = AppointmentService.find_appointment(db=db, appointment=appointment)
    
    if existing:
        logger.error("POST: ❌ Такая запись уже существует ❌")
        raise HTTPException(status_code=400, detail="Такая запись уже существует")
    
    new_appointment = await AppointmentService.create_appointment(db=db, appointment=appointment)
        
    return new_appointment
        
@router.put("/{appointment_id}", response_model=schemas.AppointmentResponse)
async def update_appointment(appointment_id: int, new_appointment: schemas.AppointmentCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Поступил запрос: PUT /appointments/{appointment_id}")
    logger.info(f"PUT: Поиск записи с id: {appointment_id} в базе данных...")
    
    appointment = await AppointmentService.get_appointment_by_id(db=db, appointment_id=appointment_id)
    
    if not appointment:
        logger.error(f"PUT: ❌ Запись с id: {appointment_id} не найдена в бд ❌")
        raise HTTPException(status_code=404, detail="Такая запись не найдена")
    
    await AppointmentService.update_appointment(
                                                 db=db, 
                                                 appointment_id=appointment_id, 
                                                 new_appointment=new_appointment, 
                                                 appointment=appointment
                                               )
    
    return appointment
    
@router.delete("/{appointment_id}", response_model=schemas.AppointmentResponse)
async def delete_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"Поступил запрос: DELETE /appointments/{appointment_id}")
    logger.info(f"DELETE: Поиск записи с id: {appointment_id} в базе данных...")
    
    appointment = await AppointmentService.get_appointment_by_id(db=db, appointment_id=appointment_id)
    
    if not appointment:
        logger.error(f"DELETE: ❌ Запись с id: {appointment_id} не найдена в бд ❌")
        raise HTTPException(status_code=404, detail="Такая запись не найдена")
    
    await AppointmentService.delete_appointment(db=db, appointment=appointment, appointment_id=appointment_id)
    return {"succes": True}