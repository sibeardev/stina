FROM python:3.14-slim

WORKDIR /opt
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

COPY . .

EXPOSE 8000
