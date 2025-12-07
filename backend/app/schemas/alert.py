from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AlertCreate(BaseModel):
    file_id: int
    process_name: str
    pid: int
    anomaly_score: float
    ml_confidence: Optional[float] = None
    label: str
    message: str


class AlertRead(AlertCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True



