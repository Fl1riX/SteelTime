import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.presentation.api.v1.endpoints import router as endpoints_router
from src.presentation.api.v1.auth.auth import router as auth_router
from src.presentation.api.v1.auth.tg_link import router as tg_link_router
from src.logger import logger
from src.limiter import limiter
from src.presentation.middlewares import MetricsMiddleware
from src.infrastructure.tasks.cleanup_magic_tokens import cleanup_telegram_tokens

app = FastAPI(
    title="SteelTime", 
    version="0.0.1", 
    description="Система для бронирования услуг",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
app.state.limiter = limiter
app.add_middleware(MetricsMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.include_router(endpoints_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tg_link_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_origins=[
        "http://localhost:3000",      
        "http://localhost:5173",      
        "http://localhost:8080",      
        "http://127.0.0.1:5500",      
        "http://localhost:5000",      
    ],
    allow_credentials=True
)

scheduler = AsyncIOScheduler() # Планировщик
@app.on_event("startup")
async def startup():
    scheduler.add_job(
        cleanup_telegram_tokens,
        "interval",
        minutes=5
    )
    scheduler.start()

@app.get("/")
@limiter.limit("5/minute")
def welcome(request: Request):
    logger.info("Получен запрос: GET /")
    return{
        "message": "Добро пожаловать в SteelTime",
        "detail": "Документация http://localhost:8000/docs"
    }

if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=True)