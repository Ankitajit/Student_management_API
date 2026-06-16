from fastapi import Header, HTTPException, Depends
from app.schemas import UserResponse
from app.database import get_db
from app.models import DBAuditLog
from sqlalchemy.orm import Session


def get_current_user(x_user_role: str = Header(default="user", description="Enter role: admin, manager, or employee")):
    clean_role = x_user_role.strip().lower()
    return UserResponse(username=f"{clean_role}", role=clean_role)

def verify_role(allowed_roles: list[str]):
    def role_checker(current_user: UserResponse = Depends(get_current_user)):
        clean_allowed = [r.lower() for r in allowed_roles]
        
        if current_user.role not in clean_allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. your role '{current_user.role}' does not have permission to perform this action."
            )
        return current_user
    return role_checker

def create_audit_log(db: Session, username: str, action: str):
    log_entry = DBAuditLog(username=username, action=action)
    db.add(log_entry)
    db.commit()