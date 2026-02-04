from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Request

from src.schemas import appointment_schema
from src.logger import logger
from src.db.database import get_db
from src.limiter import limiter
from src.services.appointments_service import AppointmentService
from src.api.v1.auth.dependencies import get_current_user_id

router = APIRouter(prefix="/appointments", tags=["Записи"])

@router.get("/{appointment_id}", response_model=appointment_schema.AppointmentResponse)
@limiter.limit("5/minute")
async def get_appointment(
    request: Request,
    appointment_id: int, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Поступил запрос: GET /appointments/{appointment_id}")
    logger.info(f"GET: Поиск записи с id: {appointment_id} в базе данных...")
    
    appointment = await AppointmentService.get_appointment_by_id(db=db, appointment_id=appointment_id)
    if not appointment:
        logger.error(f"GET: ❌ Запись с id: {appointment_id} не найдена в бд ❌")
        raise HTTPException(status_code=404, detail="Запись не найдена")

    logger.info(f"GET: Запись с id: {appointment_id} успешно найдена в бд ✅")

    if current_user_id != appointment.user_id and current_user_id != appointment.entrepreneur_id:
        logger.warning(f"Пользователь с id: {current_user_id} пытается получить данные о чужой записи")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этим данным"
        )

    return appointment

@router.post("/", response_model=appointment_schema.AppointmentResponse)
@limiter.limit("5/minute")
async def create_appointment(
    request: Request,
    appointment: appointment_schema.AppointmentCreate, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    logger.info("Поступил запрос: POST /appointments/")
    logger.info("POST: Проверка наличия записи в бд...")
    
    existing = await AppointmentService.find_appointment(db=db, appointment=appointment, current_user_id=current_user_id)
    
    if existing:
        logger.error("POST: ❌ Такая запись уже существует ❌")
        raise HTTPException(status_code=400, detail="Такая запись уже существует")
    
    new_appointment = await AppointmentService.create_appointment(db=db, appointment=appointment, current_user_id=current_user_id)
        
    return new_appointment
        
@router.put("/{appointment_id}", response_model=appointment_schema.AppointmentResponse)
@limiter.limit("3/minute")
async def update_appointment(
    request: Request,
    appointment_id: int, 
    new_appointment: appointment_schema.AppointmentCreate, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Поступил запрос: PUT /appointments/{appointment_id}")
    logger.info(f"PUT: Поиск записи с id: {appointment_id} в базе данных...")
    
    appointment = await AppointmentService.get_appointment_by_id(db=db, appointment_id=appointment_id)
    
    if not appointment:
        logger.error(f"PUT: ❌ Запись с id: {appointment_id} не найдена в бд ❌")
        raise HTTPException(status_code=404, detail="Такая запись не найдена")
    
    if current_user_id != appointment.entrepreneur_id:
        logger.warning(f"Пользователь с id: {current_user_id} пытается изменить данные о записи({appointment_id}) предпринимателя: {appointment.entrepreneur_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этой записи"
        )
    
    await AppointmentService.update_appointment(
        db=db, 
        appointment_id=appointment_id, 
        new_appointment=new_appointment, 
        appointment=appointment
    )
    
    return appointment
    
@router.delete("/{appointment_id}")
@limiter.limit("5/minute")
async def delete_appointment(
    request: Request,
    appointment_id: int, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Поступил запрос: DELETE /appointments/{appointment_id}")
    logger.info(f"DELETE: Поиск записи с id: {appointment_id} в базе данных...")
    
    appointment = await AppointmentService.get_appointment_by_id(db=db, appointment_id=appointment_id)
    
    if not appointment:
        logger.error(f"DELETE: ❌ Запись с id: {appointment_id} не найдена в бд ❌")
        raise HTTPException(status_code=404, detail="Такая запись не найдена")
    
    if current_user_id != appointment.entrepreneur_id and current_user_id != appointment.user_id:
        logger.warning(f"Пользователь с id: {current_user_id} пытается удалить чужую запись: {appointment_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этой записи"
        )
    
    await AppointmentService.delete_appointment(db=db, appointment=appointment, appointment_id=appointment_id)
    return {"success": True}