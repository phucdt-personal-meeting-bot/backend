import asyncio

from core.celery_app import celery_app
from crud.translation_job import get_job, update_job_status
from db.session import AsyncSessionLocal
import models  # noqa: F401 — register all models so FK resolution works
from models.translation_job import JobStatus


@celery_app.task(name="tasks.translation.run_translation")
def run_translation(job_id: int) -> None:
    asyncio.run(_run_translation(job_id))


async def _run_translation(job_id: int) -> None:
    async with AsyncSessionLocal() as db:
        job = await get_job(db, job_id)
        if not job:
            return

        try:
            await update_job_status(db, job, JobStatus.processing)

            # TODO: add translation logic here
            print("Running translation for job", job_id)

            await update_job_status(db, job, JobStatus.completed)
        except Exception as e:
            await update_job_status(db, job, JobStatus.failed, error=str(e))
