from datetime import datetime, timezone
from typing import List

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.infrastructure.db.database import Base
from src.logger import logger
from src.domain.models.ban_model import Ban
from src.domain.models.appointment_model import Appointment
from src.domain.models.magic_token_model import MagicToken
from src.domain.models.service_model import Service

class User(Base):
    """
    Таблица пользователя
      id: int, primary_key=True
      telegram_id: int, unique=True, nullable=True
      telegram_linked_at: datetime | None, default=None
      username: str(50), nullable=False
      phone: str(30), unique=True, nullable=False
      email: str(50), unique=True
      password: str(255), nullable=False
      created_at: datetime, default=datetime.now(timezone.utc)
      is_entrepreneur: bool, default=False
      full_name: str(150) | None
      my_appointments: relationship [Appointment.user_id]
      users_appointments: relationship [Appointment.entrepreneur_id]
      services: relationship
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=True)
    telegram_linked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(150))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_entrepreneur: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(Enum("user", "admin", "moderator"), default="user", name="user_role")

    bans: Mapped[List["Ban"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[Ban.user_id]",
    )
    my_appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[Appointment.user_id]",
    )
    users_appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="entrepreneur",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="[Appointment.entrepreneur_id]",
    )
    services: Mapped[List["Service"]] = relationship(
        back_populates="entrepreneur",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    magic_tokens: Mapped[List["MagicToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @validates("created_at")
    def validate_create_date(self, key, value):
        if not isinstance(value, datetime) and value is not None:
            logger.warning("Некорректная дата")
            raise TypeError("Некорректная дата")
        elif value > datetime.utcnow():
            logger.warning("Дата регистрации не может быть в будущем")
            raise ValueError("Дата регистрации не может быть в будущем")
        return value
