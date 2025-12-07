from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String

from app.db.session import Base


class MemoryFile(Base):
    __tablename__ = "memory_files"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256 = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)



