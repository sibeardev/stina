from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from tests.helpers import set_booking_status

from app.domain import BookingStatus


class TestCreateBooking:
    async def test_create_booking_returns_201(
        self,
        client: AsyncClient,
        booking_payload: dict[str, str],
    ) -> None:
        response = await client.post("/bookings", json=booking_payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == booking_payload["name"]
        assert data["service_type"] == booking_payload["service_type"]
        assert data["status"] == BookingStatus.PENDING.value
        assert data["id"]
        assert data["created_at"]

    async def test_create_booking_rejects_empty_name(
        self,
        client: AsyncClient,
        booking_payload: dict[str, str],
    ) -> None:
        booking_payload["name"] = "   "

        response = await client.post("/bookings", json=booking_payload)

        assert response.status_code == 422

    async def test_create_booking_rejects_past_datetime(
        self,
        client: AsyncClient,
        booking_payload: dict[str, str],
    ) -> None:
        past = datetime.now(UTC) - timedelta(hours=1)
        booking_payload["datetime"] = past.isoformat()

        response = await client.post("/bookings", json=booking_payload)

        assert response.status_code == 422

    async def test_create_booking_rejects_naive_datetime(
        self,
        client: AsyncClient,
        booking_payload: dict[str, str],
    ) -> None:
        naive = datetime(2026, 12, 1, 12, 0, 0)
        booking_payload["datetime"] = naive.isoformat()

        response = await client.post("/bookings", json=booking_payload)

        assert response.status_code == 422


class TestListBookings:
    async def test_list_bookings_empty(self, client: AsyncClient) -> None:
        response = await client.get("/bookings")

        assert response.status_code == 200
        data = response.json()
        assert data == {"items": [], "total": 0, "offset": 0, "limit": 20}

    async def test_list_bookings_returns_created_items(
        self,
        client: AsyncClient,
        created_booking: dict,
    ) -> None:
        response = await client.get("/bookings")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == created_booking["id"]

    async def test_list_bookings_filters_by_status(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        booking_payload: dict[str, str],
    ) -> None:
        first = await client.post("/bookings", json=booking_payload)
        second_payload = {**booking_payload, "name": "Anna"}
        second = await client.post("/bookings", json=second_payload)
        await set_booking_status(
            db_session,
            second.json()["id"],
            BookingStatus.CONFIRMED,
        )

        pending_response = await client.get("/bookings", params={"status": "pending"})
        confirmed_response = await client.get(
            "/bookings",
            params={"status": "confirmed"},
        )

        assert pending_response.status_code == 200
        assert confirmed_response.status_code == 200
        assert pending_response.json()["total"] == 1
        assert pending_response.json()["items"][0]["id"] == first.json()["id"]
        assert confirmed_response.json()["total"] == 1
        assert confirmed_response.json()["items"][0]["id"] == second.json()["id"]

    async def test_list_bookings_pagination(
        self,
        client: AsyncClient,
        booking_payload: dict[str, str],
    ) -> None:
        for index in range(3):
            payload = {**booking_payload, "name": f"Guest {index}"}
            response = await client.post("/bookings", json=payload)
            assert response.status_code == 201

        page = await client.get("/bookings", params={"offset": 1, "limit": 1})

        assert page.status_code == 200
        data = page.json()
        assert data["total"] == 3
        assert data["offset"] == 1
        assert data["limit"] == 1
        assert len(data["items"]) == 1

    async def test_list_bookings_offset_beyond_total(
        self,
        client: AsyncClient,
        created_booking: dict,
    ) -> None:
        response = await client.get("/bookings", params={"offset": 10})

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"] == []

    @pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}])
    async def test_list_bookings_rejects_invalid_pagination(
        self,
        client: AsyncClient,
        params: dict[str, int],
    ) -> None:
        response = await client.get("/bookings", params=params)

        assert response.status_code == 422
