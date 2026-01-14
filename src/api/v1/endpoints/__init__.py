from fastapi import APIRouter
from . import users, entrepreneurs, services, appointments

router = APIRouter()

router.include_router(users.router)
router.include_router(entrepreneurs.router)
router.include_router(services.router)
router.include_router(appointments.router)