FROM python:3.11-slim as base

LABEL maintainer="theabdyko@gmail.com" \
    version="1.0" \
    description="Production-ready app for b2broker"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PYTHONPATH="${PYTHONPATH}:/app"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN pip install --no-cache-dir poetry==1.7.1

FROM base as dependencies
COPY pyproject.toml poetry.lock ./

RUN poetry install --only=main --no-root \
    && rm -rf $POETRY_CACHE_DIR

FROM dependencies as production

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base as develop

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root \
    && rm -rf $POETRY_CACHE_DIR

COPY . .

RUN groupadd -r devuser && useradd -r -g devuser devuser \
    && chown -R devuser:devuser /app

USER devuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
