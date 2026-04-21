import math

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from models.translation_job import JobStatus, TranslationJob
from schemas.translation import SheetPrompt


async def create_job(
    db: AsyncSession,
    user_id: int,
    language: str,
    prompt: str,
    sheet_prompts: list[SheetPrompt],
    file_key: str,
    bucket: str,
) -> TranslationJob:
    job = TranslationJob(
        user_id=user_id,
        status=JobStatus.pending,
        language=language,
        prompt=prompt,
        sheet_prompts=[sp.model_dump() for sp in sheet_prompts],
        file_key=file_key,
        bucket=bucket,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_job(db: AsyncSession, job_id: int) -> TranslationJob | None:
    result = await db.execute(select(TranslationJob).where(TranslationJob.id == job_id))
    return result.scalar_one_or_none()


async def get_jobs_by_user(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[TranslationJob], int]:
    base = select(TranslationJob).where(TranslationJob.user_id == user_id)

    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar_one()

    items_result = await db.execute(
        base
        .order_by(TranslationJob.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(items_result.scalars().all())

    return items, total


async def update_job_status(
    db: AsyncSession,
    job: TranslationJob,
    status: JobStatus,
    result_file_key: str | None = None,
    error: str | None = None,
) -> TranslationJob:
    job.status = status
    if result_file_key is not None:
        job.result_file_key = result_file_key
    if error is not None:
        job.error = error
    await db.commit()
    await db.refresh(job)
    return job
