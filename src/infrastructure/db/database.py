from sqlalchemy.orm import declarative_base
from fastapi import Request

Base = declarative_base()

async def get_db(request: Request):
    
    async with request.app.state.SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()



