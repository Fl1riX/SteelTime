import httpx
from src.logger import logger
from src.shared.schemas.bot.tg_link import TgLinkStatus

async def check_registration(user_id: str) -> TgLinkStatus:
    """Проверяет привязку телеграм аккаунта"""
    result = TgLinkStatus(connected=False, is_entrepreneur=False)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=10.0)) as client:
            response = await client.get(f"http://localhost:8000/api/v1/users/check_tg_link/{user_id}")

            if response.status_code == 200:
                data = response.json()
                logger.debug(data)
                return TgLinkStatus(
                    connected=data.get("connected", False),
                    is_entrepreneur=data.get("is_entrepreneur", False)
                )
            else:
                logger.warning(f"Server error: {response.status_code}")
                return result
            
    except httpx.ReadTimeout:
        logger.error("❌ Error: API сервер не доступен ❌")
        return result
    except Exception as e:
        logger.error(f"❌ Error: {e} ❌")
        return result