from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import redis
import uuid
import os

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379)


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.hset(f"job:{job_id}", "status", "queued")
    r.lpush("jobs", job_id)
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": status.decode()}


@app.get("/health")
def health():
    try:
        r.ping()
        return {"status": "ok"}
    except Exception:
        return JSONResponse(status_code=503,
                            content={"status": "redis unavailable"})
