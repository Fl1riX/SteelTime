from fastapi import APIRouter
from src.api.v1.endpoints import users, services, appointments

router = APIRouter()

router.include_router(users.router)
router.include_router(services.router)
router.include_router(appointments.router)