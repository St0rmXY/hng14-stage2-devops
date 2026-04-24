#!/usr/bin/env bash
set -euo pipefail

STACK_UP=0
EXIT_CODE=0

cleanup() {
  if [ "$STACK_UP" -eq 1 ]; then
    echo "==> Tearing down stack..."
    docker compose down -v --remove-orphans || true
  fi
}
trap cleanup EXIT

echo "==> Starting stack..."
docker compose up --build -d
STACK_UP=1

echo "==> Waiting for API..."
for i in $(seq 1 30); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || true)
  if [ "$STATUS" = "200" ]; then
    echo "    API healthy after $i attempts"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "ERROR: API did not become healthy in time"
    exit 1
  fi
  sleep 3
done

echo "==> Waiting for frontend..."
for i in $(seq 1 30); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health || true)
  if [ "$STATUS" = "200" ]; then
    echo "    Frontend healthy after $i attempts"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "ERROR: Frontend did not become healthy in time"
    exit 1
  fi
  sleep 3
done

echo "==> Submitting job..."
RESPONSE=$(curl -s -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"payload": "integration-test"}')
echo "    Response: $RESPONSE"

JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
if [ -z "$JOB_ID" ]; then
  echo "ERROR: No job_id returned"
  exit 1
fi
echo "    Job ID: $JOB_ID"

echo "==> Polling for job completion..."
for i in $(seq 1 30); do
  RESPONSE=$(curl -s http://localhost:8000/jobs/$JOB_ID)
  STATUS=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "unknown")
  echo "    Attempt $i - status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    echo "==> Job completed successfully!"
    exit 0
  fi

  if [ "$STATUS" = "failed" ]; then
    echo "ERROR: Job failed"
    exit 1
  fi

  sleep 3
done

echo "ERROR: Job did not complete within timeout"
exit 1
