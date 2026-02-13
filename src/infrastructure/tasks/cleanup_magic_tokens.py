from sqlalchemy import select, delete

from .get_db import SessionLocal
from src.domain.db.models import MagicTokens
from src.logger import logger

async def cleanup_telegram_tokens():
    """Очистка истекших токенов"""
    async with SessionLocal() as db:
        logger.info("Поиск использованных токенов привязки телеграм...")
        result = await db.execute(select(MagicTokens).where(
            MagicTokens.used == True
        ))
        used_tokens = result.scalars().all()
        if used_tokens:
            logger.info("Найдены недействительные токены")
            try:
                await db.execute(delete(MagicTokens).where(
                    MagicTokens.used == True
                ))
                await db.commit()
                logger.info("✅ Недействительные токены были удалены ✅")
            except Exception as e:
                logger.info(f"❌ Ошибка: {e} ❌")
                raise
        else:
            logger.info("✅ Ненайдено недействительных токенов ✅")