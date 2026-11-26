FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app.py ./
COPY static ./static

EXPOSE 8000
CMD sh -c "uv run --no-sync uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"
