FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY config config/
COPY src src/
COPY scripts scripts/

RUN pip install --upgrade pip && pip install -e ".[api]"

RUN mkdir -p data/raw phases/phase-0 phases/phase-1 phases/phase-2 \
    phases/phase-3 phases/phase-4 phases/phase-5 phases/phase-6

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"

CMD uvicorn src.api.app:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}
