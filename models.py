from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class DBRecord(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    department = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBAuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(200), nullable=False)
    action = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)