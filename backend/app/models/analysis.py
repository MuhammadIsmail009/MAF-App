from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Float
from sqlalchemy.orm import relationship

from app.db.session import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("memory_files.id"), nullable=False, index=True)
    status = Column(String, default="completed", nullable=False)
    summary = Column(String, nullable=True)
    volatility_output = Column(JSON, nullable=True)
    ml_output = Column(JSON, nullable=True)
    dl_output = Column(JSON, nullable=True)
    max_anomaly_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    file = relationship("MemoryFile")



