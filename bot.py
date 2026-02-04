import asyncio

from aiogram import Bot, Dispatcher

from src.bot.config import TELEGRAM_BOT_TOKEN
from src.bot.handlers.start import router as start_router
from src.logger import logger

bot = Bot(token=str(TELEGRAM_BOT_TOKEN))
dp = Dispatcher()

dp.include_router(start_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("🔄 Webhook удален, запуск polling...")
    
    logger.info("✅ Бот запущен! ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try: 
        logger.info("Запуск бота...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ Бот останлен пользователем ⛔")
