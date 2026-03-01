# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY license_server/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
# Copy specific folders from root context
COPY license_server ./license_server/
COPY shared ./shared/

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

WORKDIR /app/license_server

# Script to wait for DB and run migrations
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000
