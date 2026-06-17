from unittest.mock import patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking
from app.domain.enums import BookingStatus
from app.schemas import BookingCreateRequest
from app.services.booking import BookingService


@pytest.fixture
async def pending_booking(
    db_session: AsyncSession,
    booking_payload: dict[str, str],
) -> Booking:
    request = BookingCreateRequest.model_validate(booking_payload)
    booking = Booking(**request.model_dump())
    db_session.add(booking)
    await db_session.flush()
    await db_session.refresh(booking)
    return booking


class TestConfirmBookingWorker:
    async def test_confirm_booking_success(
        self,
        db_session: AsyncSession,
        pending_booking: Booking,
    ) -> None:
        with (
            patch(
                "app.services.booking.should_fail_external_service",
                return_value=False,
            ),
            patch("app.services.booking.send_notification") as mock_notify,
        ):
            await BookingService(db_session).confirm(pending_booking.id)

        await db_session.refresh(pending_booking)
        assert pending_booking.status == BookingStatus.CONFIRMED
        mock_notify.assert_called_once_with(
            pending_booking.name,
            str(pending_booking.id),
        )

    async def test_confirm_booking_external_failure(
        self,
        db_session: AsyncSession,
        pending_booking: Booking,
    ) -> None:
        with (
            patch(
                "app.services.booking.should_fail_external_service",
                return_value=True,
            ),
            patch("app.services.booking.send_notification") as mock_notify,
        ):
            await BookingService(db_session).confirm(pending_booking.id)

        await db_session.refresh(pending_booking)
        assert pending_booking.status == BookingStatus.FAILED
        mock_notify.assert_not_called()

    async def test_confirm_booking_is_idempotent_for_confirmed(
        self,
        db_session: AsyncSession,
        pending_booking: Booking,
    ) -> None:
        pending_booking.status = BookingStatus.CONFIRMED
        await db_session.flush()

        with patch("app.services.booking.send_notification") as mock_notify:
            await BookingService(db_session).confirm(pending_booking.id)

        await db_session.refresh(pending_booking)
        assert pending_booking.status == BookingStatus.CONFIRMED
        mock_notify.assert_not_called()

    async def test_confirm_booking_skips_missing_booking(
        self,
        db_session: AsyncSession,
    ) -> None:
        with patch("app.services.booking.send_notification") as mock_notify:
            await BookingService(db_session).confirm(uuid4())

        mock_notify.assert_not_called()
