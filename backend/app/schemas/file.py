from datetime import datetime
from pydantic import BaseModel


class MemoryFileBase(BaseModel):
    case_id: str
    filename: str
    size_bytes: int
    sha256: str


class MemoryFileCreate(BaseModel):
    case_id: str


class MemoryFileRead(MemoryFileBase):
    id: int
    stored_path: str
    created_at: datetime

    class Config:
        from_attributes = True



