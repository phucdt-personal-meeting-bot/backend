from enum import Enum

from pydantic import BaseModel


class Language(str, Enum):
    vi = "vi"
    en = "en"
    ja = "ja"


class SheetPrompt(BaseModel):
    sheet_name: str
    prompt: str


class TranslationUploadResponse(BaseModel):
    file_key: str
    bucket: str
    language: Language
    prompt: str
    sheet_prompts: list[SheetPrompt]
