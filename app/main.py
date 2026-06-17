from contextlib import asynccontextmanager

from fastapi import FastAPI
import taskiq_fastapi

from app.api.router import router
from app.core.config import settings
from app.worker.broker import broker

taskiq_fastapi.init(broker, "app.main:app")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not broker.is_worker_process:
        await broker.startup()
    yield
    if not broker.is_worker_process:
        await broker.shutdown()


app = FastAPI(
    debug=settings.debug,
    title="Stina",
    description="Backend service for making appointments",
    lifespan=lifespan,
)

app.include_router(router)
