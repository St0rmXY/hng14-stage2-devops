from fastapi 
import FastAPI
import redis
import uuid
import os
import HTTPException

app = FastAPI()
REDIS_HOST = os.getenv("REDIS_HOST", "rediis")
r = redis.Redis(host=REDIS_HOST, port=6379)

@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("job", job_id)i
    r.hset(f"job:{job_id}", "status", "queued")
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        raise HTTPException{status_code=404, detail=" Job not found"}
    return {"job_id": job_id, "status": status.decode()}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
