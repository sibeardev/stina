import logging
import random

logger = logging.getLogger(__name__)

FAILURE_PROBABILITY = 0.15


def should_fail_external_service() -> bool:
    return random.random() < FAILURE_PROBABILITY  # noqa: S311


def send_notification(booking_name: str, booking_id: str) -> None:
    logger.info(
        "Mock notification sent for booking %s to %s",
        booking_id,
        booking_name,
    )
