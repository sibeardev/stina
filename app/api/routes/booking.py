from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import BookingServiceDep
from app.domain.enums import BookingStatus
from app.schemas import BookingCreateRequest, BookingListResponse, BookingResponse
from app.worker.tasks import confirm_booking_task

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=BookingResponse,
)
async def create_booking(
    payload: BookingCreateRequest,
    service: BookingServiceDep,
) -> BookingResponse:
    booking = await service.create(payload)
    await confirm_booking_task.kiq(str(booking.id))
    return BookingResponse.model_validate(booking)


@router.get("", response_model=BookingListResponse)
async def list_bookings(
    service: BookingServiceDep,
    status: BookingStatus | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> BookingListResponse:
    return await service.list_bookings(status=status, offset=offset, limit=limit)


@router.get("/{booking_id}", response_model=BookingStatus)
async def get_booking_status(
    booking_id: UUID,
    service: BookingServiceDep,
) -> BookingStatus:
    booking_status = await service.get_booking_status(booking_id)
    if not booking_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    return booking_status


@router.delete("/{booking_id}", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    service: BookingServiceDep,
) -> BookingResponse:
    try:
        booking = await service.cancel(booking_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    return BookingResponse.model_validate(booking)
