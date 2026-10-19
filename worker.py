import os
import time
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

print("Worker listening for jobs...")

while True:
    # brpop blocks until an item appears in 'job_queue' (timeout 5s)
    task = r.brpop("job_queue", timeout=5)
    if task:
        _, job_id = task
        print(f"Processing job: {job_id}")
        r.hset(f"job:{job_id}", "status", "processing")
        
        # Simulate heavy work (e.g. data crunching or video conversion)
        time.sleep(5)
        
        r.hset(f"job:{job_id}", mapping={"status": "completed", "result": "Success!"})
        print(f"Finished job: {job_id}")