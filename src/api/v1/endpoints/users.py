from src.schemas import user_schema
from src.logger import logger
from src.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Пользователи"])

@router.get("/{user_id}", response_model=user_schema.UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"GET: Получен запрос: GET /users/{user_id}")
    logger.info(f"GET: Проверка наличия пользователя с id: {user_id} в бд...")
    
    user = await UserService.find_user_by_id(id=user_id, db=db)
    
    if not user:
        logger.error(f"GET: Пользователь с id: {user_id} не найден")
        raise HTTPException(status_code=404, detail=f"Пользователь не найден")
    
    logger.info(f"GET: Найден пользователь с id: {user_id} ✅")
    return user

@router.put("/{user_id}", response_model=user_schema.UserResponse)
async def update_user(user_id: int, new_user: user_schema.UserRegister, db: AsyncSession = Depends(get_db)):
    logger.info(f"PUT: Получен запрос: PUT /users/{user_id}")
    logger.info(f"PUT: Проверка наличия пользователя с id: {user_id} в бд...")
    
    user = await UserService.find_user_by_id(id=user_id, db=db)
    
    if not user:
        logger.error(f"PUT: ❌ Пользователь с id: {user_id} не найден в бд ❌")
        raise HTTPException(status_code=404, detail="Нельзя обновить даные. Такого пользователя не существует")
    
    logger.info(f"PUT: Пользователь с id: {user_id} найден в бд. Обновление данных...")
    
    await UserService.update_user(new_user=new_user, db=db, user=user)
    
    return user

@router.delete("/{user_id}")
async def delet_user(user_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"DELETE: Получен запрос: DELETE /users/{user_id}")
    logger.info(f"DELETE: Проверка наличия пользователя с id: {user_id} в бд...")
    
    user = await UserService.find_user_by_id(id=user_id, db=db)
    
    if not user:
        logger.error(f"DELETE: ❌ Пользователь с id: {user_id} не найден в бд ❌")
        raise HTTPException(status_code=404, detail="Такого пользователя не существует")
    
    logger.info(f"DELETE: Пользователь с id: {user_id} найден в бд. Удаляем данные...")
    
    await UserService.delte_user(db=db, user=user)
    
    return {"succes": True}
    