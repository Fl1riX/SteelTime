from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from typing import List
from .database import Base
from datetime import datetime, timezone
from src.logger import logger

class User(Base): # пользователь
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(25), unique=True, index=True, nullable=True) # для поиска использует B-дерево, что ускоряет его
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    is_entrepreneur: Mapped[bool] = mapped_column(default=False)
    full_name: Mapped[str | None] = mapped_column(String(150))
    my_appointments: Mapped[List["Appointment"]] = relationship(
                                                              back_populates="user",
                                                              cascade="all, delete-orphan", # каскадная операция, при удалении удалятся все связанные данные
                                                              lazy="selectin", # загружает все через два оптимизированных запроса, контролирует когда загружать связанные данные
                                                              foreign_keys="[Appointment.user_id]"
                                                            ) # ссылаеся на записи 
    users_appointments: Mapped[List["Appointment"]] = relationship(
                                                              back_populates="entrepreneur",
                                                              cascade="all, delete-orphan",
                                                              lazy="selectin",
                                                              foreign_keys="[Appointment.entrepreneur_id]"
                                                            ) # ссылаемся на таблицу с записями
    services: Mapped[List["Service"]] = relationship(
                                                      back_populates="entrepreneur",
                                                      cascade="all, delete-orphan",
                                                      lazy="selectin"
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
    
class Service(Base): # услуга
    __tablename__ = "services"
    __table_args__ = (
      UniqueConstraint(
        "name",
        "address",
        "entrepreneur_id",
        name="uq_name_address_entrepreneur_id",
      ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    price: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(2000))
    duration: Mapped[str] = mapped_column(String(10), nullable=False) # продолжительость в часах
    address: Mapped[str] = mapped_column(String(100))
    entrepreneur_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    entrepreneur: Mapped["User"] = relationship(
                                                          back_populates="services",
                                                          lazy="selectin"
                                                        )
    appointments: Mapped[List["Appointment"]] = relationship(
                                                               back_populates="service",
                                                               cascade="all, delete-orphan",
                                                               lazy="selectin"
                                                             )

class Appointment(Base): # запись 
    __tablename__ = "appointments"
    # не позволяет создавать записи с одинаковыми данными в полях
    __table_args__ = (
      UniqueConstraint(
        "service_id",
        "entrepreneur_id",
        "user_id",
        "date",
        name="uq_appointment_service_entrepreneur_user_date",
      ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    comment: Mapped[str] = mapped_column(String(1200))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id")) # сохраняем какую услугу оказываем, чтобы service могла сослаться на таблицу
    service: Mapped["Service"] = relationship(
                                               back_populates="appointments",
                                               lazy="selectin"
                                            )
    entrepreneur_id: Mapped[int] = mapped_column(ForeignKey("users.id")) # id исполнителя
    entrepreneur: Mapped["User"] = relationship(
                                                         back_populates="users_appointments",
                                                         lazy="selectin",
                                                         foreign_keys=[entrepreneur_id] # явно указываем внешний ключ, чтобы небыло ошибок
                                                       ) # ссылаемся на предринимателя
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
                                         back_populates="my_appointments",
                                         lazy="selectin",
                                         foreign_keys=[user_id]
                                       ) # ссылаемся на пользователя
    
    @validates("date")
    def validate_date(self, key, value):
      if not isinstance(value, datetime) and value is not None:
        logger.warning("Некорректная дата")
        raise TypeError("Некорректная дата")
      elif value < datetime.utcnow():
        logger.warning("Дата оказания услуги не может быть в прошлом")
        raise ValueError("Дата оказания услуги не может быть в прошлом")