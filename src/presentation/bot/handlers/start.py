from aiogram import types, Router
from aiogram.filters.command import Command

from src.logger import logger
from ..keyboards import start_keyboards
from src.domain.services.tg_client import check_registration

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
    
    if not tg_linked.connected:
        await message.answer(f"Приветствуем, вас {name}, в чатботе сервиса SteelTime. Привяжите бота к аккаунту серваса или зарегистрируйтесь, чтобы получать отсюда уведомления и напоминания, связанные с вашими записями", reply_markup=start_keyboards.link_keyboard)
    else: 
        if tg_linked.is_entrepreneur:
            await message.answer(f"👋 Рады, вас {name}, снова видеть, в чат-боте нашего сервиса SteelTime!", reply_markup=start_keyboards.entrepreneur_start_keyboard)
        else:
            await message.answer(f"👋 Рады, вас {name}, снова видеть, в чат-боте нашего сервиса SteelTime!", reply_markup=start_keyboards.user_start_keyboard)
        
