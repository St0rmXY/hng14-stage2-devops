import redis
import time
import os
import signal
import sys

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=REDIS_HOST, port=6379)


def process_job(job_id):
    try:
        print(f"Processing job {job_id}")
        r.hset(f"job:{job_id}", "status", "processing")
        time.sleep(2)
        r.hset(f"job:{job_id}", "status", "completed")
        print(f"Done: {job_id}")
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        r.hset(f"job:{job_id}", "status", "failed")


def handle_shutdown(signum, frame):
    print("Shutting down worker gracefully...")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

while True:
    job = r.brpop("jobs", timeout=5)
    if job:
        _, job_id = job
        process_job(job_id.decode())
    with open("/tmp/worker_healthy", "w") as f:
        f.write("ok")
