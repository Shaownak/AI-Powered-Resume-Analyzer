import time

from ai.scorer import calculate_resume_score
from cache.redis_cache import cache
from celery import Celery

# Celery configuration
celery_app = Celery("resume_tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

# Celery configuration settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


def score_resume_async(resume_text: str, job_description: str) -> str:
    """
    Start async task to score resume and return task ID
    """
    try:
        # Start the Celery task
        task = score_resume_task.delay(resume_text, job_description)
        return task.id
    except Exception as exc:
        print(f"❌ Failed to start async task: {exc}")
        # Fallback to synchronous scoring if Redis/Celery unavailable
        try:
            score = calculate_resume_score(resume_text, job_description)
            result_score = round(score * 100, 2)
            return {
                "score": result_score,
                "cached": False,
                "task_id": "sync_fallback",
                "timestamp": time.time(),
                "status": "completed",
            }
        except Exception as fallback_exc:
            print(f"❌ Fallback scoring also failed: {fallback_exc}")
            raise exc


def get_task_result(task_id: str) -> dict:
    """
    Get result of async task by task ID
    """
    if task_id == "sync_fallback":
        return {"status": "completed", "result": task_id}

    try:
        # Get task result from Celery
        task = score_resume_task.AsyncResult(task_id)

        if task.ready():
            if task.successful():
                return {"status": "completed", "result": task.result}
            else:
                return {"status": "failed", "error": str(task.info)}
        else:
            return {"status": "pending", "meta": task.info}
    except Exception as exc:
        print(f"❌ Failed to get task result: {exc}")
        return {"status": "error", "error": str(exc)}


@celery_app.task(bind=True)
def score_resume_task(self, resume_text: str, job_description: str) -> dict:
    """
    Async task to score resume with caching
    """
    try:
        # Generate cache key
        cache_key = cache.get_score_cache_key(resume_text, job_description)

        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            print(f"✅ Cache hit for task {self.request.id}")
            return {"score": cached_result["score"], "cached": True, "task_id": self.request.id}

        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "Processing resume..."})

        # Calculate score
        score = calculate_resume_score(resume_text, job_description)
        result_score = round(score * 100, 2)

        # Cache result for 1 hour
        result = {"score": result_score, "cached": False, "task_id": self.request.id, "timestamp": time.time()}

        cache.set(cache_key, result, expiry=3600)
        print(f"✅ Scored and cached result for task {self.request.id}: {result_score}%")

        return result

    except Exception as exc:
        print(f"❌ Task {self.request.id} failed: {exc}")
        self.update_state(state="FAILURE", meta={"error": str(exc), "task_id": self.request.id})
        raise exc


@celery_app.task
def cleanup_old_cache_entries():
    """
    Periodic task to clean up old cache entries
    """
    try:
        # This would require more complex Redis operations
        # For now, Redis TTL handles cleanup automatically
        print("✅ Cache cleanup task completed")
        return {"status": "completed", "timestamp": time.time()}
    except Exception as exc:
        print(f"❌ Cache cleanup failed: {exc}")
        raise exc
