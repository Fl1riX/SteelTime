import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.endpoints import router as endpoints_router
from src.api.v1.auth import router as auth_router
from src.logger import logger

app = FastAPI(title="Service Booking System", version="0.0.1", description="Система для бронирования услуг")
app.include_router(endpoints_router, prefix="/api/v1")
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_origins = ["*"],
    allow_credentials=True
)

@app.get("/")
def wellcome():
    logger.info("Получен запрос: GET /")
    return{
        "message": "Добро пожаловать в Service-Booking-System",
        "detail": "Документация http://localhost:8000/docs"
    }

if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=True)