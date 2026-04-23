from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Language(str, Enum):
    vi = "vi"
    en = "en"
    ja = "ja"


class SheetPrompt(BaseModel):
    sheet_name: str
    prompt: str


class PaginatedJobsResponse(BaseModel):
    items: list["TranslationJobResponse"]
    total: int
    page: int
    page_size: int
    pages: int


class TranslationJobResponse(BaseModel):
    id: int
    status: str
    language: str
    prompt: str
    sheet_prompts: list[SheetPrompt]
    file_key: str
    bucket: str
    result_file_key: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobDownloadResponse(BaseModel):
    original_url: str
    result_url: str | None = None
