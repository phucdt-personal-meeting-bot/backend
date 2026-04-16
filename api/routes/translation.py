import json
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status

from api.deps import get_current_user
from core.s3 import BUCKET_NAME, ensure_bucket_exists, get_s3_client
from models.user import User
from schemas.translation import Language, SheetPrompt, TranslationUploadResponse

ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",  # .xls
}

router = APIRouter(prefix="/translation", tags=["translation"])


@router.post("/upload", response_model=TranslationUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload(
    file: UploadFile,
    language: Language = Form(...),
    prompt: str = Form(...),
    sheet_prompts: str = Form(..., description='JSON array, e.g. [{"sheet_name":"Sheet1","prompt":"..."}]'),
    current_user: User = Depends(get_current_user),
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

    return TranslationUploadResponse(
        file_key=file_key,
        bucket=BUCKET_NAME,
        language=language,
        prompt=prompt,
        sheet_prompts=parsed_sheet_prompts,
    )
