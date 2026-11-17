from celery import Celery

from src.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "credlens_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.workers.assessment_worker"],
)

# Robust celery config settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Johannesburg",  # Locked to South African timezone for reporting schedules
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes maximum runtime for external integration jobs
    worker_concurrency=4,  # Concurrency limit based on lightweight task profile
    result_expires=86400,
    broker_connection_retry_on_startup=True,
    broker_connection_timeout=3,
    task_publish_retry=False,
)

# Task registration is explicit through the include list above.
