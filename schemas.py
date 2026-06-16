from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecordBase(BaseModel):
    title: str
    description: Optional[str] = None
    department: str

class RecordCreate(RecordBase):
    pass

class RecordResponse(RecordBase):
    id: int

    class Config:
        from_attributes = True



class AuditLogResponse(BaseModel):
    id: int
    username: str
    action: str
    timestamp: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    username: str
    role: str