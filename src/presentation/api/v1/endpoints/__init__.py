from src.presentation.api.v1.endpoints.appointments import router as appointment_router
from src.presentation.api.v1.endpoints.services import router as services_router
from src.presentation.api.v1.endpoints.users import router as user_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(appointment_router)
router.include_router(services_router)
router.include_router(user_router)
