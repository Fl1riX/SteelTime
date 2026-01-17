from src.schemas import service_schema
from src.logger import logger
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from src.services.service_service import ServiceService

router = APIRouter(prefix="/services", tags=["Услуги"])

@router.get("/{service_id}", response_model=service_schema.ServiceResponse)
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"GET: Получен запрос: GET /services/{service_id}")
    logger.info(f"GET: Поиск услуги с id: {service_id} в бд...")
    
    service = await ServiceService.find_service_by_id(id=service_id, db=db)
    
    if not service:
        logger.error(f"GET: Услуга с id: {service_id} не найдена")
        raise HTTPException(status_code=404, detail="Такая услуга не найдена")
    
    logger.error(f"GET: Услуга с id: {service_id} найдена ✅")
    return service

@router.post("/", response_model=service_schema.ServiceResponse)
async def create_service(service: service_schema.ServiceCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Получен запрос: POST /services/")
    logger.info("POST: Проверка наличия услуги в бд...")
    
    existing = await ServiceService.find_by_name(service=service, db=db)
    
    if existing:
        logger.error("POST: такая услуга уже существует")
        raise HTTPException(status_code=400, detail="Такая услуга уже существует")
    
    logger.info("POST: Услуга не найдена в бд ✅. Запись данных...")
    new_service = await ServiceService.create_service(service=service, db=db)
    
    return new_service

@router.delete("/{service_id}")
async def delete_service(service_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"DELETE: Получен запрос: DELETE /services/{service_id}")
    logger.info(f"DELETE: Проверка наличия услуги с id: {service_id} в бд...")
    
    service = await ServiceService.find_service_by_id(id=service_id, db=db)
    
    if not service:
        logger.error(f"DELETE: Такой услуги не существует в бд")
        raise HTTPException(status_code=404, detail="Такой услуги не существует")
    
    await ServiceService.delete_service(service=service, db=db)
    
    return {"succes": True}
    
@router.put("/{service_id}", response_model=service_schema.ServiceResponse)
async def update_service(new_service: service_schema.ServiceCreate, service_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"PUT: Получен запрос: PUT /services/{service_id}")
    logger.info("PUT: Проверка наличия услуги в бд...")
    
    service = await ServiceService.find_service_by_id(id=service_id, db=db)
    
    if not service:
        logger.error("PUT: Такая услуга не найдена")
        raise HTTPException(status_code=404, detail="Такая услуга не найдена")
    
    logger.info("PUT: Услуга найдена ✅. Обновление данных...")
    
    await ServiceService.update_service(new_service=new_service, db=db, service=service)
    
    return service