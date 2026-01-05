from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

DB_URL = "sqlite+aiosqlite:///./Booking-System.db"

engine = create_async_engine(
    DB_URL, 
    connect_args={"check_same_thread": False}, 
    echo=True # для отладки 
)

SessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()



