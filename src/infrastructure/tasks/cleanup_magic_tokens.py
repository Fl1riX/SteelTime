from sqlalchemy import select, delete, or_
from datetime import datetime, timezone

from .get_db import SessionLocal
from src.domain.db.models import MagicTokens
from src.logger import logger

async def cleanup_telegram_tokens():
    """Очистка истекших токенов"""
    async with SessionLocal() as db:
        logger.info("🔍 Очистка токенов...")
        try:
            await db.execute(delete(MagicTokens).where(
            or_(
                MagicTokens.used == True,
                MagicTokens.expires_at < datetime.now(timezone.utc)
            )
            ))
            await db.commit()
            logger.info("✅ Недействительные токены были удалены ✅")
        except Exception as e:
            logger.info(f"❌ Ошибка: {e} ❌")
            raise
        else:
            logger.info("✅ Ненайдено недействительных токенов ✅")