from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status, Request

from src.schemas import service_schema
from src.logger import logger
from src.db.database import get_db
from src.services.service_service import ServiceService
from src.api.v1.auth.dependencies import get_current_user_id
from src.limiter import limiter

router = APIRouter(prefix="/services", tags=["Услуги"])

@router.get("/{service_id}", response_model=service_schema.ServiceResponse)
@limiter.limit("5/minute")
async def get_service(
    request: Request,
    service_id: int, 
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"GET: Получен запрос: GET /services/{service_id}")
    
    logger.info(f"GET: Поиск услуги с id: {service_id} в бд...")
    service = await ServiceService.find_service_by_id(id=service_id, db=db)
    
    if not service:
        logger.error(f"GET: Услуга с id: {service_id} не найдена")
        raise HTTPException(status_code=404, detail="Такая услуга не найдена")
    
    logger.info(f"GET: Услуга с id: {service_id} найдена ✅")
    return service

@router.post("/", response_model=service_schema.ServiceResponse)
@limiter.limit("5/minute")
async def create_service(
    request: Request,
    service: service_schema.ServiceCreate, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    logger.info("Получен запрос: POST /services/")
    logger.info("POST: Проверка наличия услуги в бд...")
    existing = await ServiceService.find_by_name(name=service.name, address=service.address, current_user_id=current_user_id, db=db)
    
    if existing:
        logger.error("POST: такая услуга уже существует")
        raise HTTPException(status_code=400, detail="Такая услуга уже существует")
    
    logger.info("POST: Услуга не найдена в бд ✅. Запись данных...")
    new_service = await ServiceService.create_service(service=service, current_user_id=current_user_id, db=db)
    
    return new_service

@router.delete("/{service_id}")
@limiter.limit("5/minute")
async def delete_service(
    request: Request,
    service_id: int, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"DELETE: Получен запрос: DELETE /services/{service_id}")
    logger.info(f"DELETE: Проверка наличия услуги с id: {service_id} в бд...")
    
    service = await ServiceService.find_service_by_id(id=service_id, db=db)
    
    if not service:
        logger.error("DELETE: Такой услуги не существует в бд")
        raise HTTPException(status_code=404, detail="Такой услуги не существует")
    
    if service.entrepreneur_id != current_user_id:
        logger.warning(f"Пользователь  с id: {current_user_id} пытается удалить услугу пользователя: {service.entrepreneur_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этой услуге"
        )
    
    await ServiceService.delete_service(service=service, db=db)
    
    return {"success": True}
    
@router.put("/{service_id}", response_model=service_schema.ServiceResponse)
@limiter.limit("5/minute")
async def update_service(
    request: Request,
    new_service: service_schema.ServiceCreate, 
    service_id: int, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"PUT: Получен запрос: PUT /services/{service_id}")
    logger.info("PUT: Проверка наличия услуги в бд...")
    
    service = await ServiceService.find_service_by_id(id=service_id, db=db)
    
    if not service:
        logger.error("PUT: Такая услуга не найдена")
        raise HTTPException(status_code=404, detail="Такая услуга не найдена")
    
    if service.entrepreneur_id != current_user_id:
        logger.warning(f"Пользователь  с id: {current_user_id} пытается удалить услугу пользователя: {service.entrepreneur_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этой услуге"
        )
    
    logger.info("PUT: Услуга найдена ✅. Обновление данных...")
    
    await ServiceService.update_service(new_service=new_service, db=db, service=service)
    
    return service