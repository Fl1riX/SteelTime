#from pathlib import Path
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from fastapi import Request

Base = declarative_base()

async def get_db(request: Request):
    
    SessionLocal = async_sessionmaker(
        bind=request.app.state.engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()



