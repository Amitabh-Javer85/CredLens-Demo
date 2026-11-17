import asyncio
from src.services.assessment_service import assess_sample
from src.workers.celery_app import celery_app

@celery_app.task(name="src.workers.assessment_worker.orchestrate_underwriting")
def orchestrate_underwriting(applicant_id: str) -> dict:
    """Execute the same mock pipeline as the CLI in a background worker."""
    return asyncio.run(assess_sample(applicant_id))
