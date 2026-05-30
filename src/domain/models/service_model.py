from typing import List

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.database import Base
from src.domain.models.user_model import User
from src.domain.models.appointment_model import Appointment


class Service(Base):
    """
      Таблица услуг (Service)
        id: int, primary_key=True
        name: str(100), nullable=False, index=True
        price: int, nullable=False
        description: str(2000)
        duration: str(10), nullable=False — длительность услуги
        address: str(100)
        entrepreneur_id: int, ForeignKey("users.id")
        entrepreneur: relationship [User] (back_populates="services", lazy="selectin")
        appointments: relationship [Appointment] (back_populates="service", cascade="all, delete-orphan", lazy="selectin")
        UniqueConstraint: (name, address, entrepreneur_id) — уникальность услуги для данного предпринимателя по названию и адресу
    """

    __tablename__ = "services"
    __table_args__ = (
        UniqueConstraint(
            "name",
            "address",
            "entrepreneur_id",
            name="uq_name_address_entrepreneur_id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(2000))
    duration: Mapped[str] = mapped_column(String(10), nullable=False)
    address: Mapped[str] = mapped_column(String(100))
    entrepreneur_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    entrepreneur: Mapped["User"] = relationship(
        back_populates="services",
        lazy="selectin",
        foreign_keys=[entrepreneur_id],
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
