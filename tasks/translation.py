import asyncio
import uuid

from core.celery_app import celery_app
from core.s3 import BUCKET_NAME, get_s3_client
from crud.translation_job import get_job, update_job_status
from db.session import AsyncSessionLocal, engine
import models  # noqa: F401
from models.translation_job import JobStatus
from services.excel import extract_text_cells, write_translations
from services.translator import translate_sheet


@celery_app.task(name="tasks.translation.run_translation")
def run_translation(job_id: int) -> None:
    asyncio.run(_run_translation(job_id))


async def _run_translation(job_id: int) -> None:
    try:
        async with AsyncSessionLocal() as db:
            job = await get_job(db, job_id)
            if not job:
                return

            try:
                await update_job_status(db, job, JobStatus.processing)

                s3 = get_s3_client()
                obj = s3.get_object(Bucket=job.bucket, Key=job.file_key)
                file_bytes = obj["Body"].read()

                sheet_cells = extract_text_cells(file_bytes)

                sheet_prompt_map = {sp["sheet_name"]: sp["prompt"] for sp in job.sheet_prompts}

                translations = {}
                for sheet_name, cells in sheet_cells.items():
                    if not cells:
                        continue
                    print(f'[Job {job_id}] Translating sheet "{sheet_name}" ({len(cells)} cells)')
                    translated = translate_sheet(
                        language=job.language,
                        file_prompt=job.prompt,
                        sheet_name=sheet_name,
                        sheet_prompt=sheet_prompt_map.get(sheet_name),
                        cells=cells,
                    )
                    translations[sheet_name] = translated

                output_bytes = write_translations(file_bytes, translations)

                result_key = f"translations/{uuid.uuid4()}/translated_{job.file_key.split('/')[-1]}"
                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=result_key,
                    Body=output_bytes,
                    ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

                print(f"[Job {job_id}] Done. Result: {result_key}")
                await update_job_status(db, job, JobStatus.completed, result_file_key=result_key)

            except Exception as e:
                print(f"[Job {job_id}] Failed: {e}")
                await update_job_status(db, job, JobStatus.failed, error=str(e))
    finally:
        await engine.dispose()
