import uvicorn
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, filename="./logs/api.log")
app = FastAPI(title="Nail appointment system", version="0.0.1", description="Система обработки заказов для бизнеса по маникюру")

app.add_middleware(
    CORSMiddleware,
    allow_headers = ["*"],
    allow_methods = ["*"],
    allow_origins = ["*"],
    allow_credentials=True
)

@app.get("/")
def wellcome():
    return{
        "message": "Добро пожаловать в Nail Booking",
        "detail": "Докуументация http://localhost:8000/docs"
    }

if __name__ == "__main__":
    uvicorn.run(app, port=8000, reload=True)