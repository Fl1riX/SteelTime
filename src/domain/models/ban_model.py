from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.infrastructure.db.database import Base
from src.domain.models.user_model import User


class Ban(Base):
    __tablename__ = "bans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reason: Mapped[str] = mapped_column(String(150), nullable=False, comment="Причина бана")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, comment="ID пользователя, который получил бан")
    banned_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, comment="Тот, кто выдал бан")
    revoked_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, comment="Тот, кто снял бан")

    banned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), comment="Время окончания бана")
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), comment="Время отмены бана")
    revoked_reason: Mapped[str | None] = mapped_column(String(150), comment="Причина отмены бана")

    moderator: Mapped["User"] = relationship(
        foreign_keys=[banned_by],
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        lazy="selectin",
        back_populates="bans",
        foreign_keys=[user_id],
    )

    revoker: Mapped["User | None"] = relationship(
        foreign_keys=[revoked_by],
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint(
            "expires_at IS NULL OR expires_at > banned_at",
            name="ck_ban_expires_after_banned",
        ),
        CheckConstraint(
            "revoked_at IS NULL OR (revoked_at >= banned_at AND (expires_at IS NULL OR revoked_at <= expires_at))",
            name="ck_ban_revoke_logic",
        ),
        Index(
            "uq_active_ban",
            "user_id",
            unique=True,
            postgresql_where=(
                revoked_at.is_(None)
                & (expires_at.is_(None) | (expires_at > func.now()))
            ),
        ),
    )

    @property
    def is_active(self) -> bool:
        if self.revoked_at is not None:
            return False

        if self.expires_at is None:
            return True

        return self.expires_at > datetime.now(timezone.utc)

    @validates("expires_at")
    def validate_expires_at(self, key, value):
        if value is not None:
            if value <= datetime.now(timezone.utc):
                raise ValueError("expires_at не должно быть в прошлом или None")
            if value <= self.banned_at:
                raise ValueError("expires_at не может быть меньше banned_at")
        return value

    @validates("banned_at")
    def validate_banned_at(self, key, value):
        if value > datetime.now(timezone.utc):
            raise ValueError("banned_at не должно быть в будущем")
        return value

    @validates("revoked_at")
    def validate_revoked_at(self, key, value):
        if value is None:
            return value

        if value > datetime.now(timezone.utc):
            raise ValueError("revoked_at не должно быть в будущем")

        if self.banned_at is not None:
            if value < self.banned_at:
                raise ValueError("banned_at не должно быть позже revoked_at")

        return value
