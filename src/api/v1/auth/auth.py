import schemas

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt_handler import create_access_token, verify_password, hash_password

from db.database import get_db
from services.user_service import UserService
from logger import logger

router = APIRouter(prefix="/auth", tags=["Авторизация"])

@router.post("/register", response_model=schemas.RegisterResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    logger.info("Получен запрос: POST /auth/register")
    logger.info("POST: Проверка наличия пользователя в бд...")
    
    if await UserService.check_user_exists(user=user, db=db):
        logger.error(f"POST: Такой пользователь уже существует в бд")
        raise HTTPException(status_code=400, detail="Такой пользователь уже существует")
    
    logger.info("POST: Такой пользователь не найден ✅. Запись данных  в бд...")
    hashed_password = hash_password(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    new_user = await UserService.create_user(user=user, db=db) # вносим данные пользователя в базу данных
    
    token = create_access_token({"sub": new_user.id})
    
    return {
            "user": new_user,
            "token": token,
            "token_type": "bearer"
            }
    
@router.get("/login", response_model=schemas.UserResponse)
async def login_user(user: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    logger.info("Получен запрос: GET /auth/register")
    logger.info("POST: Проверка наличия пользователя в бд...")
    user_exists = await UserService.check_user_exists(user=user, db=db)
    
    # проверяем регистрацию пользователя
    if not user_exists:
        logger.error(f"POST: Такой пользователь не существует в бд")
        raise HTTPException(status_code=404, detail="Неверный email или пароль")
    
    # проверяем корректность введенного пароля
    if not verify_password(password=user.password, hashed_password=user_exists.password):
        logger.info(f"Введен не верный пароль пользователя: {user.email}")
        raise HTTPException(status_code=404, detail="Неверный email или пароль")  
    
    token = create_access_token({"sub": user.id})
    
    return {
        "user_id": user.id,
        "token": token,
        "token_type": "bearer"
    }
    