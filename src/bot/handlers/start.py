import httpx

from aiogram import types, Router
from aiogram.filters.command import Command

from src.logger import logger

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    if message.from_user:
        name = message.from_user.full_name or message.from_user.first_name
        user_id = message.from_user.id
    else:
        name = "Пользователь"
        user_id = "Unknown"
    
    logger.info(f"📩 Полученно сообщение от пользователя: {user_id}")
    tg_linked = await check_registration(str(user_id))
    if tg_linked:
        await message.answer(f"👋 Рады, вас {name}, снова видеть, в чат-боте нашего сервиса SteelTime!")
    else:
        await message.answer(f"Приветствуем, вас {name}, в чатботе сервиса SteelTime. Привяжите бота к аккаунту серваса или зарегистрируйтесь, чтобы получать отсюда уведомления и напоминания, связанные с вашими записями")

async def check_registration(user_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/api/v1/users/check_tg_link/{user_id}", 
                timeout=httpx.Timeout(5.0, read=10.0) 
            )

            if response.status_code == 200:
                data = response.json()
                return dict(data)["connected"]
            else:
                logger.warning(f"Server error: {response.status_code}")
                return False
            
    except httpx.ReadTimeout:
        logger.error("❌ Error: API сервер не доступен ❌")
    except Exception as e:
        logger.error(f"❌ Error: {e} ❌")