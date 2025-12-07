from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ProcessPrediction(BaseModel):
    pid: int
    ppid: int
    name: str
    anomaly_score: float
    confidence: float
    label: str  # benign / malicious
    features: Dict[str, Any]


class AnalysisResultRead(BaseModel):
    id: int
    file_id: int
    status: str
    summary: Optional[str]
    volatility_output: Optional[Dict[str, Any]]
    ml_output: Optional[Dict[str, Any]]
    dl_output: Optional[Dict[str, Any]]
    max_anomaly_score: float
    created_at: datetime
    processes: Optional[List[ProcessPrediction]] = None

    class Config:
        from_attributes = True



