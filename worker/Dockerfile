# hadolint ignore=DL3008
FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# hadolint ignore=DL3013,DL3042
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.13-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --chown=appuser:appgroup . .

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "\
import os, redis; \
r = redis.Redis(host=os.getenv('REDIS_HOST','redis'), port=6379); \
r.ping()" || exit 1

CMD ["python", "worker.py"]
