from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DBAuditLog
from app.schemas import AuditLogResponse, UserResponse
from app.dependencies import verify_role
from typing import List

router = APIRouter(prefix="/audit-logs", tags=["Audit System"])

@router.get("/", response_model=List[AuditLogResponse], summary="Verify Audit Logs (Admin Only)")
def get_logs(db: Session = Depends(get_db), current_user: UserResponse = Depends(verify_role(["Admin"]))):
    return db.query(DBAuditLog).order_by(DBAuditLog.timestamp.desc()).all()
