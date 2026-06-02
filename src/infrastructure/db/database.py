from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker
)

Base = declarative_base()

SessionLocal: async_sessionmaker[AsyncSession] | None = None

async def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database is not initialied")
    async with SessionLocal() as session:
            yield session



