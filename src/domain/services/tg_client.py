import httpx
from async_lru import alru_cache

from src.logger import logger
from src.shared.schemas.bot.tg_link import TgLinkStatus

@alru_cache(maxsize=512, ttl=300) # кэширование, хранить максимум 512 результатов, удалсять через 300 секунд
async def check_registration(user_id: str) -> TgLinkStatus:
    """Проверяет привязку телеграм аккаунта"""
    result = TgLinkStatus(connected=False, is_entrepreneur=False)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=10.0)) as client:
            logger.info("Отправка запроса к api...")
            response = await client.get(f"http://localhost:8000/api/v1/users/check_tg_link/{user_id}")

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Получен ответ от api: {data}")
                return TgLinkStatus(
                    connected=data.get("connected", False),
                    is_entrepreneur=data.get("is_entrepreneur", False)
                )
            else:
                logger.warning(f"❌ Server error: {response.status_code} ❌")
                return result
            
    except httpx.ReadTimeout:
        logger.error("❌ Error: API сервер не доступен ❌")
        return result
    except Exception as e:
        logger.error(f"❌ Error: {e} ❌")
        return result
    
@alru_cache(maxsize=512, ttl=300)
async def get_user_profile(user_id: str):
    """Получает информацию о пользователе"""
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=10.0)) as client:
            response = await client.get(f"http://localhost:8000/api/v1/users/{user_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.info(f"Ошибка получения информации о профиле пользователя: {response.status_code}")
        
    except httpx.ReadTimeout:
        logger.error("❌ Error: API сервер не доступен ❌")
    except Exception as e:
        logger.error(f"❌ Error: {e} ❌")
    
async def generate_magic_token(tg_id: int) -> str | None:
    """Отправляет запрос к api на создание magic токена"""
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=10.0)) as client:
            logger.info(f"Отвправка запроса на генерацию magic токна для пользователя: {tg_id}...")
            response = await client.get(f"http://127.0.0.1:8000/api/v1/auth/telegram/generate-link/{tg_id}")
            
            if response.status_code == 200:
                data = response.json()
                link_token = data.get("token", None)
                logger.info(f"Тоекн для привязки акканута {tg_id}: {link_token}")
                return link_token
            else:
                return None
        
    except httpx.ReadTimeout:
        logger.error("❌ Error: API сервер не доступен ❌")
        return None
    except Exception as e:
        logger.error(f"❌ Error: {e} ❌")
        return None