from sqlalchemy import delete, or_
from datetime import datetime, timezone

from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import MagicToken
from src.logger import logger

async def cleanup_telegram_tokens():
    """Очистка истекших токенов"""
    async with SessionLocal() as db:
        logger.info("🔍 Очистка токенов...")
        try:
            await db.execute(delete(MagicToken).where(
            or_(
                MagicToken.used,
                MagicToken.expires_at < datetime.now(timezone.utc)
            )
            ))
            await db.commit()
            logger.info("✅ Недействительные токены были удалены ✅")
        except Exception as e:
            logger.info(f"❌ Ошибка: {e} ❌")
            raise