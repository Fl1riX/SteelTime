from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

DB_PATH = BASE_DIR / "Booking-System.db"
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

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