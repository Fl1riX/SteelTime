import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from src.presentation.api.v1.endpoints import router as endpoints_router
from src.presentation.api.v1.auth.auth import router as auth_router
from src.logger import logger
from src.limiter import limiter

app = FastAPI(
    title="SteelTime", 
    version="0.0.1", 
    description="Система для бронирования услуг",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.include_router(endpoints_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

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