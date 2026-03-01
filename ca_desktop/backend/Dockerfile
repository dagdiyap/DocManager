# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY ca_desktop/backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# runtime tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
# Copy specific folders from root context
COPY ca_desktop/backend ./ca_desktop/backend/
COPY shared ./shared/

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

WORKDIR /app/ca_desktop/backend

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8443"]
