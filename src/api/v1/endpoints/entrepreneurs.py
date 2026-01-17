from src import schemas
from src.logger import logger
from src.db.database import get_db
from src.db import models
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from src.services.entrepreneurs_service import EntrepreneurService

router = APIRouter(prefix="/entrepreneurs", tags=["Предприниматели"])

@router.get("/{user_id}", response_model=schemas.EntrepreneurResponse)
async def get_user(user_id:  int, db: AsyncSession = Depends(get_db)):
    logger.info(f"GET: Получен запрос: GET /entrepreneurs/{user_id}")
    logger.info(f"GET: Поиск пользователя с id: {user_id} в бд...")
    
    entrepreneur = await EntrepreneurService.get_entrepreneur_by_id(db=db, user_id=user_id)
    if not entrepreneur:
        logger.info("GET: Искомый пользовател не существует в бд")
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    logger.info(f"GET: Найден пользователь: {entrepreneur.full_name}, {entrepreneur.id}✅")
    return entrepreneur

@router.post("/", response_model=schemas.EntrepreneurResponse)
async def create_entrepreneur(entrepreneur: schemas.EntrepreneurCreate, db: AsyncSession = Depends(get_db)):
    logger.info("POST: Получен запрос: POST /entrepreneurs/")
    logger.info("POST: Проверка наличия пользователя в бд...")
    
    existing = await EntrepreneurService.find_entrepreneur(db=db, enterpreneur=entrepreneur)
    
    if existing:
        logger.error(f"POST: Такой пользователь уже существует в бд: {entrepreneur.telegram_id} с id: {existing.id}")
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")
    
    new_entrepreneur = models.Entrepreneur(**entrepreneur.dict())
    await EntrepreneurService.create_entrepreneur(db=db, new_entrepreneur=new_entrepreneur)
    
    return new_entrepreneur

@router.put("/{entrepreneur_id}", response_model=schemas.EntrepreneurResponse)
async def update_entrepreneur(new_entrepreneur: schemas.EntrepreneurCreate, entrepreneur_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"PUT: Получен запрос: PUT /entrepreneurs/{entrepreneur_id}")
    logger.info(f"PUT: Проверка наличия пользователя с id: {entrepreneur_id} в бд")
    
    entrepreneur = await EntrepreneurService.get_entrepreneur_by_id(db=db, user_id=entrepreneur_id)
    
    if not entrepreneur:
        logger.error("PUT: Пользователь не найден.")
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    for key, value in new_entrepreneur.dict().items():
        if hasattr(entrepreneur, key) and value is not None:
            setattr(entrepreneur, key, value)
    
    await EntrepreneurService.update_entrepreneur(db=db, entrepreneur_id=entrepreneur_id, new_entrepreneur=new_entrepreneur)
    
    return entrepreneur

@router.delete("/{entrepreneur_id}")
async def delete_entrepreneur(entrepreneur_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"DELETE: Получен запрос: DELETE /entrepreneurs/{entrepreneur_id}")
    logger.info("DELETE: Проверка наличия пользователя в бд...")
    
    entrepreneur = await EntrepreneurService.get_entrepreneur_by_id(db=db, user_id=entrepreneur_id)
    
    if not entrepreneur:
        logger.error(f"DELETE: Пользователь с id: {entrepreneur_id} не найден в бд")
        raise HTTPException(status_code=400, detail="Такого пользователя не существует")
    
    await EntrepreneurService.delete_entrepreneur(db=db, entrepreneur=entrepreneur)
    
    return {"succes": True}
    
    