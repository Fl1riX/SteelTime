from aiogram import Router, F
from aiogram.types import Message

#from src.presentation.bot.keyboards import start_keyboards
from src.logger import logger
from src.domain.services.tg_client import get_user_profile

router = Router()

@router.message(F.text == "🚹 Мой профиль 💎")
async def my_profile(message: Message):
    if message.from_user:
        user_id = message.from_user.id
    user_data = await get_user_profile(str(user_id))
    if not user_data:
        await message.answer("Ошибка. Данные не найдены")
        logger.info(f"Ошибка. Нет данных о профиле пользователя: {user_id}")
    else:
        await message.answer(user_data)
        
    