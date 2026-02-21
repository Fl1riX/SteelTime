import asyncio

from logging.config import fileConfig
from src.infrastructure.db.database import Base
from src.infrastructure.db.models import User, Service, Appointment  # noqa: F401
from src.config import DATABASE_URL

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", f"postgresql+asyncpg://{DATABASE_URL}") # Меняем ссылку на БД, беря ее не из .ini файла

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def do_run_migrations(connection):
    """Синхронная функция, которая получает уже готовое соединение и выполняет миграции
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction(): # Открывает транзакцию, если в процессе миграции что-то пойдет не так, то все откатится
        context.run_migrations()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    asyncio.run(run_async_migrations()) # Запускаем фасинхронную функцию из sync контекста

async def run_async_migrations():
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = async_engine_from_config( # делаем асинхронный движок, читая настройки из конфига
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool, # Не держим пул соединений
    )
    
    async with connectable.connect() as connection: # Открывает асинхронное соединение, после выхода закрывается автоматически
        await connection.run_sync(do_run_migrations) # Запускаем синхронную функцию do_run_migrations внутри async кода, передавая ей sync версию соединения
    
    await connectable.dispose() # явно освобождаем ресурсы engine после завершения

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
