from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("memory_files.id"), nullable=False, index=True)
    process_name = Column(String, nullable=False)
    pid = Column(Integer, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    ml_confidence = Column(Float, nullable=True)
    label = Column(String, nullable=False)  # benign / malicious
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    file = relationship("MemoryFile")



