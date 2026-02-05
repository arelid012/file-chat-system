from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    EXCEL = "excel"

class FileBase(BaseModel):
    filename: str
    original_filename: str
    file_type: FileType
    file_size: int

class FileCreate(FileBase):
    session_id: str
    text_content: Optional[str] = None

class FileResponse(FileBase):
    id: str = Field(alias="_id")
    session_id: str
    text_content: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class FileInDB(FileResponse):
    pass