# глобальные фикстуры(это функции подготовки данных/окружения, которые автоматически запускаются ПЕРЕД ВСЕМИ тестами в проекте.)  для БД, API
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.infrastructure.db.models import Base

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Создаем сессию для тестов"""
    DB_URL = "sqlite+aiosqlite:///:memory:"
    # Создаем движок
    engine = create_async_engine(
        DB_URL,
        echo=True
    )
    SessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async with SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    # Закрываем после всех тестов
    await engine.dispose()

