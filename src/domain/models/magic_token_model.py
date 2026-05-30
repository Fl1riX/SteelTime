from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.database import Base
from src.domain.models.user_model import User

class MagicToken(Base):
    """Магические токены для привязки аккаунта к телеграм боту.

    Таблица, хранящая magic токены для привязки телеграм бота
      id: int, primary_key
      telegram_id: int, nullable=False
      token: str(64), nullable=False, unique=True
      expires_at: datetime, nullable=False
      used: bool, default=False
      created_at: datetime, default=datetime.now(timezone.utc)
    """
    __tablename__ = "magic_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False)
    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        back_populates="magic_tokens",
        foreign_keys=[user_id],
        lazy="selectin",
    )
