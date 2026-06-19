import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config

MAX_RETRIES = 10
RETRY_DELAY_SECONDS = 2


def _upgrade() -> None:
    root = Path(__file__).resolve().parents[2]
    config = Config(str(root / "alembic.ini"))
    command.upgrade(config, "head")


async def run_migrations() -> None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            await asyncio.to_thread(_upgrade)
            return
        except Exception:
            if attempt == MAX_RETRIES:
                raise
            await asyncio.sleep(RETRY_DELAY_SECONDS)
