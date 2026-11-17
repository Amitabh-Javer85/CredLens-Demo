"""Synthetic-only demo API; jobs expire after 24 hours."""
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from redis import Redis
from redis.exceptions import RedisError
from kombu.exceptions import OperationalError
from src.core.config import settings
from src.data.synthetic_applicants import SYNTHETIC_APPLICANTS
from src.workers.assessment_worker import orchestrate_underwriting
from src.workers.celery_app import celery_app

router = APIRouter()

def job_store():
    return Redis.from_url(settings.REDIS_URL, socket_connect_timeout=3, socket_timeout=3)

class ApplicationSubmitPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    applicant_id: str = "APP-DEMO-001"

@router.get("/samples")
def list_samples():
    """Select a fictional fixture; personal or bank data uploads are not accepted."""
    return {"synthetic": True, "applicants": SYNTHETIC_APPLICANTS}

@router.post("", status_code=202)
def submit_application(payload: ApplicationSubmitPayload):
    if payload.applicant_id not in SYNTHETIC_APPLICANTS:
        raise HTTPException(422, "Unknown synthetic applicant")
    task_id = str(uuid4())
    try:
        job_store().setex(f"demo-job:{task_id}", 86400, payload.applicant_id)
        orchestrate_underwriting.apply_async(args=[payload.applicant_id], task_id=task_id)
    except (RedisError, OperationalError):
        try:
            job_store().delete(f"demo-job:{task_id}")
        except RedisError:
            pass
        raise HTTPException(503, "Demo queue unavailable") from None
    return {"application_id": task_id, "status": "QUEUED"}

def get_result(application_id: UUID):
    try:
        if not job_store().exists(f"demo-job:{application_id}"):
            raise HTTPException(404, "Unknown or expired application")
        return celery_app.AsyncResult(str(application_id))
    except RedisError:
        raise HTTPException(503, "Demo queue unavailable") from None

@router.get("/{application_id}")
def get_application_status(application_id: UUID):
    result = get_result(application_id)
    try:
        state = result.state
    except RedisError:
        raise HTTPException(503, "Demo queue unavailable") from None
    return {"application_id": str(application_id), "status": state}

@router.get("/{application_id}/memo")
def get_credit_memo(application_id: UUID):
    result = get_result(application_id)
    try:
        if result.failed():
            raise HTTPException(409, "Assessment failed; submit a new demo job")
        if not result.successful():
            raise HTTPException(409, "Memo is not ready")
        return result.result
    except RedisError:
        raise HTTPException(503, "Demo queue unavailable") from None
