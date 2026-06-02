from sqlalchemy import update
from datetime import datetime, timezone

from src.domain.models.ban_model import Ban
from src.infrastructure.db.database import SessionLocal

async def remove_expired_bans():
    async with SessionLocal() as db:
        await db.execute(update(Ban).where(
                Ban.expires_at.is_not(None),
                Ban.expires_at < datetime.now(timezone.utc),
                Ban.revoked_at.is_(None)
            ).values(
                revoked_at = datetime.now(timezone.utc),
                revoked_reason="Expiration of the Term"
            )
        )
        
        await db.commit()