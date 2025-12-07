from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class ChainOfCustodyLog(Base):
    __tablename__ = "chain_of_custody_logs"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("memory_files.id"), nullable=True, index=True)
    event_type = Column(String, nullable=False)  # upload, analysis, report, hash_validation, alert
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    file = relationship("MemoryFile")



