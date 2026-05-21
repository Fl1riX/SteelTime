from sqlalchemy import String, DateTime, Boolean, Integer, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column, validates
from typing import List
from .database import Base
from datetime import datetime, timezone
from src.logger import logger

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
    
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=True) # для поиска использует B-дерево, что ускоряет его
    telegram_linked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(150))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_entrepreneur: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(Enum("user", "admin", "moderator"), default="user")
    
    bans: Mapped[List["Ban"]] = relationship(
      back_populates="user",
      cascade="all, delete-orphan",
      lazy="selectin",
      foreign_keys="[Ban.user_id]"
    )
    my_appointments: Mapped[List["Appointment"]] = relationship(
      back_populates="user",
      cascade="all, delete-orphan", # каскадная операция, при удалении удалятся все связанные данные
      lazy="selectin", # загружает все через два оптимизированных запроса, контролирует когда загружать связанные данные
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
    magic_tokens: Mapped[List["MagicToken"]] = relationship(
      back_populates="user",
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
      foreign_keys=[entrepreneur_id]
    )
    appointments: Mapped[List["Appointment"]] = relationship(
      back_populates="service",
      cascade="all, delete-orphan",
      lazy="selectin"
    )

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    comment: Mapped[str] = mapped_column(String(1200))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id")) # сохраняем какую услугу оказываем, чтобы service могла сослаться на таблицу
    service: Mapped["Service"] = relationship(
      back_populates="appointments",
      lazy="selectin",
      foreign_keys=[service_id]
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
      elif value < datetime.now(timezone.utc):
        logger.warning("Дата оказания услуги не может быть в прошлом")
        raise ValueError("Дата оказания услуги не может быть в прошлом")
      return value
      
class MagicToken(Base): # магические токены для привязки аккаунта к телеграм боту
    """
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
      foreign_keys=[user_id]
    )
    
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
  
  banner : Mapped["User"] = relationship(
    foreign_keys=[banned_by],
    lazy="selectin"
  )
  
  user: Mapped["User"] = relationship(
    lazy="selectin",
    back_populates="bans",
    foreign_keys=[user_id]
  )
  
  revoker: Mapped["User |  None"] = relationship(
    foreign_keys=[revoked_by],
    lazy="selectin"
  )
  
  @property # в реальном времени высчитываем активен ли бан или нет
  def is_active(self) -> bool:
    if self.revoked_at is not None:
      return False
    if self.expires_at is None:
      return True
    return self.expires_at > datetime.now(timezone.utc) # Вернет True или False в зависисмотсти от того, что время бана прошло или нет
  
  @validates("expires_at")
  def validate_expires_at(self, key, value):
    if value <= datetime.now(timezone.utc) and value is not None:
      raise ValueError
    return value
    
  @validates("banned_at")
  def validate_banned_at(self, key, value):
    if value > datetime.now(timezone.utc):
      raise ValueError
    return value