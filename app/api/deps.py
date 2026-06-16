from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services import BookingService

DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_booking_service(session: DbSessionDep) -> BookingService:
    return BookingService(session)


BookingServiceDep = Annotated[BookingService, Depends(get_booking_service)]
