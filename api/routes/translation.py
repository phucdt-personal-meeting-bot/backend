import asyncio
import json
import uuid

import math

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user
from tasks.translation import run_translation
from core.s3 import BUCKET_NAME, ensure_bucket_exists, generate_presigned_url, get_s3_client
from crud.translation_job import create_job, get_job, get_jobs_by_user
from db.session import get_db
from models.user import User
from schemas.translation import JobDownloadResponse, Language, PaginatedJobsResponse, SheetPrompt, TranslationJobResponse

ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",  # .xls
}

router = APIRouter(prefix="/translation", tags=["translation"])


@router.post("/upload", response_model=TranslationJobResponse, status_code=status.HTTP_201_CREATED)
async def upload(
    file: UploadFile,
    language: Language = Form(...),
    prompt: str = Form(...),
    sheet_prompts: str = Form(..., description='JSON array, e.g. [{"sheet_name":"Sheet1","prompt":"..."}]'),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only .xlsx and .xls files are accepted.",
        )

    try:
        parsed_sheet_prompts = [SheetPrompt(**item) for item in json.loads(sheet_prompts)]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='sheet_prompts must be a valid JSON array of {"sheet_name": str, "prompt": str}.',
        )

    file_key = f"translations/{uuid.uuid4()}/{file.filename}"
    contents = await file.read()

    s3 = get_s3_client()
    ensure_bucket_exists(s3)

    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=contents,
            ContentType=file.content_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to upload file to S3: {e}",
        )

    job = await create_job(
        db=db,
        user_id=current_user.id,
        language=language,
        prompt=prompt,
        sheet_prompts=parsed_sheet_prompts,
        file_key=file_key,
        bucket=BUCKET_NAME,
    )

    await asyncio.to_thread(run_translation.delay, job.id)
    return job


@router.get("/jobs", response_model=PaginatedJobsResponse)
async def list_jobs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_jobs_by_user(db, current_user.id, page, page_size)
    return PaginatedJobsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/jobs/{job_id}", response_model=TranslationJobResponse)
async def get_job_status(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await get_job(db, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job


@router.get("/jobs/{job_id}/download", response_model=JobDownloadResponse)
async def download_job_files(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await get_job(db, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    s3 = get_s3_client()
    original_url = generate_presigned_url(s3, job.bucket, job.file_key)
    result_url = generate_presigned_url(s3, job.bucket, job.result_file_key) if job.result_file_key else None

    return JobDownloadResponse(original_url=original_url, result_url=result_url)
