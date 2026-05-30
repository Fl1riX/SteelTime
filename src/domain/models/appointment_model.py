from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.infrastructure.db.database import Base
from src.domain.models.user_model import User
from src.domain.models.service_model import Service
from src.logger import logger


class Appointment(Base):
    """
      Таблица записи на услугу (Appointment)
        id: int, primary_key=True
        date: datetime (timezone=True), nullable=False, валидация: не может быть в прошлом
        comment: str(1200)
        service_id: int, ForeignKey("services.id")
        service: relationship [Service] (back_populates="appointments", lazy="selectin")
        entrepreneur_id: int, ForeignKey("users.id") — id исполнителя
        entrepreneur: relationship [User] (back_populates="users_appointments", foreign_keys=[entrepreneur_id])
        user_id: int, ForeignKey("users.id") — id клиента
        user: relationship [User] (back_populates="my_appointments", foreign_keys=[user_id])
        UniqueConstraint: (service_id, entrepreneur_id, user_id, date) — уникальность записи
    """

    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint(
            "service_id",
            "entrepreneur_id",
            "user_id",
            "date",
            name="uq_appointment_service_entrepreneur_user_date",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    comment: Mapped[str] = mapped_column(String(1200))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    service: Mapped["Service"] = relationship(
        back_populates="appointments",
        lazy="selectin",
        foreign_keys=[service_id],
    )
    entrepreneur_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    entrepreneur: Mapped["User"] = relationship(
        back_populates="users_appointments",
        lazy="selectin",
        foreign_keys=[entrepreneur_id],
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        back_populates="my_appointments",
        lazy="selectin",
        foreign_keys=[user_id],
    )

    @validates("date")
    def validate_date(self, key, value):
        if not isinstance(value, datetime) and value is not None:
            logger.warning("Некорректная дата")
            raise TypeError("Некорректная дата")
        elif value < datetime.now(timezone.utc):
            logger.warning("Дата оказания услуги не может быть в прошлом")
            raise ValueError("Дата оказания услуги не может быть в прошлом")
        return value
