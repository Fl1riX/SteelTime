from sqlalchemy import Column, Integer, String, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String(50))
    phone = Column(String(30), unique=True)

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String(2000))
    price_type = Column(String)
    duration = Column(Integer)

class Appointment(Base): # запись 
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    name = Column(String, ForeignKey("users.username"))
    comment = Column(String)
    phone = Column(String(30), ForeignKey("users.phone"))
    adress = Column(String)
    service_name = Column(String, ForeignKey("services.name"))
    service_price = Column(String, ForeignKey("services.price"))

class Entrepreneur(Base): # предприниматель
    pass