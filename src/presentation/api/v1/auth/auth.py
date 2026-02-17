from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.security import OAuth2PasswordRequestForm

from src.presentation.api.v1.auth.jwt_handler import create_access_token, verify_password, hash_password
from src.infrastructure.db.database import get_db
from src.domain.services.user_service import UserService
from src.domain.services.auth_service import AuthService
from src.domain.services.tg_link_service import TgLinkService
from src.logger import logger
from src.domain.services.exceptions import UserNotFound
from src.presentation.api.v1.auth.dependencies import get_current_user_id
from src.shared.schemas import auth_schema
from src.presentation.api.v1.exceptions import ConflictError, Unauthorized, NoAccess, NotFound, NotCorrect

router = APIRouter(prefix="/auth", tags=["Авторизация"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/login-link")
@limiter.limit("3/minute")
async def login_with_link(
    request: Request,
    login_data: auth_schema.UserLogin,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    user_data = auth_schema.UserLogin(
        login=login_data.login,
        password=login_data.password
    )
    user = await UserService.check_user_exists(user=user_data, db=db)
    
    # проверяем регистрацию пользователя
    if not user:
        logger.error("POST: Такой пользователь не существует в бд")
        raise Unauthorized("Неверный email или пароль")
    
    # Проверяем что токен есть в базе данных
    if not await TgLinkService.find_token(token, db):
        raise NotCorrect("Не верный токен")
    
    # проверяем корректность введенного пароля
    if not verify_password(password=login_data.password, hashed_password=user.password):
        logger.info(f"Введен не верный пароль для пользователя: {user_data.login}")
        raise Unauthorized("Неверный email или пароль")  
    
    logger.info(f"Поиск токена в бд: {token}...")
    link_token = await TgLinkService.check_magic_token(token, db)
    
    if not link_token:
        logger.info(f"Magic токен не найден: {token}")
        raise NotCorrect("Недействительный токен")
    
    # Привязываем id telegram к аккаунту
    await TgLinkService.link_account(db=db, link_token=link_token, user=user)
    
    return {"success": True}
    

@router.post("/register", response_model=auth_schema.UserRegisterResponse)
@limiter.limit("5/minute")
async def create_user(request: Request, user: auth_schema.UserRegister, db: AsyncSession = Depends(get_db)):
    logger.info("POST: Проверка наличия пользователя в бд...")
    
    if await AuthService.find_user_registration(user=user, db=db):
        logger.error("POST: Такой пользователь уже существует в бд")
        raise ConflictError("Такой пользователь уже существует")
    
    logger.info("POST: Такой пользователь не найден ✅. Запись данных  в бд...")
    hashed_password = hash_password(user.password)
    user_dict = user.model_dump(exclude_unset=True)
    user_dict["password"] = hashed_password
    
    new_user = await UserService.create_user(user=user_dict, db=db) # вносим данные пользователя в базу данных
    
    token = create_access_token({"sub": new_user.id})
    
    return {
            "user": new_user,
            "token": token,
            "token_type": "Bearer"
            }
    
@router.post("/login", response_model=auth_schema.UserLoginResponse)
@limiter.limit("5/minute")
async def login_user(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    logger.info("POST: Проверка наличия пользователя в бд...")
    
    user_data = auth_schema.UserLogin(
        login=form_data.username,
        password=form_data.password
    )
    user_exists = await UserService.check_user_exists(user=user_data, db=db)
    
    # проверяем регистрацию пользователя
    if not user_exists:
        logger.error("POST: Такой пользователь не существует в бд")
        raise Unauthorized("Неверный email или пароль")
    
    # проверяем корректность введенного пароля
    if not verify_password(password=form_data.password, hashed_password=user_exists.password):
        logger.info(f"Введен не верный пароль для пользователя: {user_data.login}")
        raise Unauthorized("Неверный email или пароль")  
    
    token = create_access_token({"sub": user_exists.id})
    
    return {
        "id": user_exists.id,
        "access_token": token,
        "token_type": "Bearer"
    }

@router.post("/change_password")
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    user_data: auth_schema.ChangePassword, 
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        logger.info("Проверка существования пользователя в бд...")
        user = await UserService.check_user_exists(user=user_data, db=db)
        
        if not user:
            logger.warning(f"Пользователь: {user} не найден")
            raise Unauthorized("Пользователь не найден")
        
        logger.info("Аутентификация пользователя...")
        if current_user_id != user.id:
            logger.warning(f"Пользователь: {current_user_id} пытается сменить пароль пользователя: {user.id}")
            raise NoAccess("У вас нет доступа к этому аккаунту")
        
        if not verify_password(password=user_data.current_password, hashed_password=user.password):
            logger.warning(f"Неудачная попытка смены пароля пользователю: {user.id}. Текущий пароль не верный.")
            raise NoAccess("Отказано в доступе, введен неверный пароль")
        
        logger.info("Обновление пароля пользователя...")
        await AuthService.update_user_password(db=db, user_data=user_data)
        logger.info("Пароль успешно обновлен ✅")
        
        return {"success" : True}
    except UserNotFound:
        raise NotFound("Пользователь не найден")
    
