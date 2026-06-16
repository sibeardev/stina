from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings

app = FastAPI(
    debug=settings.debug,
    title="Stina",
    description="Backend service for making appointments",
)

app.include_router(router)
