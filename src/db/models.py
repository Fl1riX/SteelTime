from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List
from src.db.database import Base
from datetime import datetime

class User(Base): # пользователь
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True) # для поиска использует B-дерево, что ускоряет его
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    appointments: Mapped[List["Appointment"]] = relationship(
                                                              back_populates="user",
                                                              cascade="all, delete-orphan", # каскадная операция, при удалении удалятся все связанные данные
                                                              lazy="selectin" # загружает все через два оптимизированных запроса, контролирует когда загружать связанные данные
                                                            ) # ссылаеся на записи 

class Entrepreneur(Base): # предприниматель
    __tablename__ = "entrepreneurs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(70), nullable=False)
    phone: Mapped[str] = mapped_column(String(25), unique=True, nullable=False, index=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    appointments: Mapped[List["Appointment"]] = relationship(
                                                              back_populates="entrepreneur",
                                                              cascade="all, delete-orphan",
                                                              lazy="selectin"
                                                            ) # ссылаемся на таблицу с записями
    services: Mapped[List["Service"]] = relationship(
                                                      back_populates="entrepreneurs",
                                                      cascade="all, delete-orphan",
                                                      lazy="selectin"
                                                    )

class Service(Base): # услуга
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    price: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(2000))
    price_type: Mapped[str] = mapped_column(String(50), nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False) # продолжительость в часах
    entrepreneur_id: Mapped[int] = mapped_column(ForeignKey("entrepreneurs.id"))
    entrepreneur: Mapped["Entrepreneur"] = relationship(
                                                          back_populates="services",
                                                          lazy="selectin"
                                                        )
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"))

class Appointment(Base): # запись 
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    comment: Mapped[str] = mapped_column(String(1200))
    address: Mapped[str] = mapped_column(String(100))
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("services.id")) # сохраняем какую услугу оказываем, чтобы service могла сослаться на таблицу
    service: Mapped["Service"] = relationship(
                                               backref="appointments",
                                               lazy="selectin"
                                            )
    entrepreneur_id: Mapped[int] = mapped_column(ForeignKey("entrepreneurs.id")) # id исполнителя
    entrepreneur: Mapped["Entrepreneur"] = relationship(
                                                         back_populates="appointments",
                                                         lazy="selectin"
                                                       ) # ссылаемся на предринимателя
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
                                         back_populates="appointments",
                                         lazy="selectin"
                                       ) # ссылаемся на пользователя