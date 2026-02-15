# глобальные фикстуры(это функции подготовки данных/окружения, которые автоматически запускаются ПЕРЕД ВСЕМИ тестами в проекте.)  для БД, API
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.domain.db.models import Base


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Создаем движок БД один раз для всех тестов"""
    
    # Создаем движок
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", 
        echo=True 
    )
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Отадаем движок
    yield test_engine
    
    # Закрываем после всех тестов
    await test_engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    """Создаем сессию для тестов"""
    
    SessionFactory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    session = SessionFactory()
    try:
        # Отдаем сессию
        yield session
    finally:
        await session.rollback()
        await session.close()
    

