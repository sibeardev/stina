from fastapi import APIRouter

from app.api.routes import booking_router

router = APIRouter()

router.include_router(booking_router)
