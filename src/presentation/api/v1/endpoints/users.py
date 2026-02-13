from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

from src.shared.schemas import user_schema
from src.logger import logger
from src.domain.db.database import get_db
from src.presentation.api.v1.auth.dependencies import get_current_user_id
from src.domain.services.user_service import UserService
from src.domain.services.auth_service import AuthService
from src.limiter import limiter
from src.presentation.api.v1.exceptions import NoAccess, NotFound

router = APIRouter(prefix="/users", tags=["Пользователи"])

@router.get("/{user_id}",  response_model=user_schema.UserResponse)
@limiter.limit("5/minute")
async def get_user(
    request: Request,
    user_id: int, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    logger.info("Аутентификация пользователя")
    if user_id != current_user_id:
        logger.warning(f"user_id: {current_user_id} пытается получить данные чужого аккаунта: {user_id}")
        raise NoAccess("У вас нет доступа к этому аккаунту") 
    
    logger.info(f"GET: Проверка наличия пользователя с id: {user_id} в бд...")
    user = await UserService.find_user_by_id(id=user_id, db=db)
    
    if not user:
        logger.error(f"GET: Пользователь с id: {user_id} не найден")
        raise NotFound("Пользователь не найден")
    
    logger.info(f"GET: Найден пользователь с id: {user_id} ✅")
    return user

@router.get("/check_tg_link/{telegram_id}")
@limiter.limit("5/minute")
async def check_user_telegram_connection(
    request: Request, 
    telegram_id: str, 
    db: AsyncSession = Depends(get_db)
):
    connected = await AuthService.check_telegram_connection(tg_id=telegram_id, db=db)
    if connected is None:
        logger.info(f"Пользователь с id: {telegram_id} не привязан к боту")
        return {"connected": False}
    
    logger.info(f"Обнаружене привязка telegram польователя с id: {telegram_id}")
    return {
        "connected": True,
        "is_entrepreneur": connected.is_entrepreneur
    }

@router.put("/{user_id}", response_model=user_schema.UserUpdate)
@limiter.limit("5/minute")
async def update_user(
    request: Request,
    user_id: int, 
    new_user: user_schema.UserUpdate, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    logger.info("Аутентификация пользователя")
    if user_id != current_user_id:
        logger.warning(f"user_id: {current_user_id} пытается изменить дынные чужого аккаунта: {user_id}")
        raise NoAccess("У вас нет доступа к этому аккаунту")
        
    logger.info(f"PUT: Проверка наличия пользователя с id: {user_id} в бд...")   
    user = await UserService.find_user_by_id(id=user_id, db=db)
    
    if not user:
        logger.error(f"PUT: ❌ Пользователь с id: {user_id} не найден в бд ❌")
        raise NotFound("Нельзя обновить даные. Такого пользователя не существует")
    
    logger.info(f"PUT: Пользователь с id: {user_id} найден в бд. Обновление данных...")
    
    await UserService.update_user(new_user=new_user, db=db, user=user)
    
    return user

@router.delete("/{user_id}")
@limiter.limit("5/minute")
async def delete_user(
    request: Request,
    user_id: int, 
    current_user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):  
    logger.info("Аутентификация пользователя")
    if user_id != current_user_id:
        logger.warning(f"user_id: {current_user_id} пытается удалить чужой аккаунт: {user_id}")
        raise NoAccess("У вас нет доступа к этому аккаунту")
    
    logger.info(f"DELETE: Проверка наличия пользователя с id: {user_id} в бд...")
    user = await UserService.find_user_by_id(id=user_id, db=db)
    
    if not user:
        logger.error(f"DELETE: ❌ Пользователь с id: {user_id} не найден в бд ❌")
        raise NotFound("Такого пользователя не существует")
    
    logger.info(f"DELETE: Пользователь с id: {user_id} найден в бд. Удаляем данные...")
    await UserService.delete_user(db=db, user=user)
    
    return {"succes": True}
    