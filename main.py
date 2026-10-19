import os
import uuid
import time
from fastapi import FastAPI, HTTPException
import redis

app = FastAPI(title="Job Processing API")

# Connect to Redis (host and port are configured via environment variables)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# 1. Health checks for Kubernetes Probes
@app.get("/live")
def liveness():
    # Only checks if the Python process itself is running
    return {"status": "alive"}

@app.get("/ready")
def readiness():
    # Checks if external dependencies (Redis) are reachable
    try:
        r.ping()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Redis connection failed")

# 2. Asynchronous Job Endpoints
@app.post("/jobs")
def create_job(task_name: str):
    job_id = str(uuid.uuid4())
    # Save the initial job state to Redis
    r.hset(f"job:{job_id}", mapping={"task": task_name, "status": "pending"})
    # Push job_id into a Redis list (the queue)
    r.lpush("job_queue", job_id)
    return {"job_id": job_id, "status": "pending"}

@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    data = r.hgetall(f"job:{job_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    return data