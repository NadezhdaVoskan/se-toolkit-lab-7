FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy

COPY bot/pyproject.toml ./pyproject.toml
COPY bot/ ./

RUN uv sync

CMD ["uv", "run", "bot.py"]
