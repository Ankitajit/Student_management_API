from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DBRecord
from app.schemas import RecordCreate, RecordResponse, UserResponse
from app.dependencies import verify_role, create_audit_log
from typing import List
from app import models, schemas


router = APIRouter(prefix="/records", tags=["Records Management"])



# 1. CREATE (Admin only)
def verify_admin(x_user_role: str = Header(..., alias="x-user-role")):
    if x_user_role.lower() != "admin":
        raise HTTPException(
            status_code=403, 
            detail="only admin"
        )
    return x_user_role

@router.post("/records/", response_model=schemas.RecordResponse, status_code=201)
def create_record(
    record: schemas.RecordCreate, 
    db: Session = Depends(get_db),
    current_role: str = Depends(verify_admin) 
):
   
    db_record = models.DBRecord(
        title=record.title, 
        description=record.description, 
        department=record.department
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record) 
    
    return db_record

# 2. READ - Search, Filter, Sort, Pagination ( Accessible to Admin, Manager, Employee)
@router.get("/", response_model=List[RecordResponse], summary=" API with Search, Filter, Sorting and Pagnation")
def read_records(
    search: str = Query(None, description=" Search records "),
    department: str = Query(None, description="Filter by department"),
    sort_by: str = Query("id", description="Select column for sorting (id, title, department)"),
    order: str = Query("asc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number (start from 1)"),
    size: int = Query(10, ge=1, max_value=100, description="Number of records per page"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(verify_role(["Admin", "Manager", "Employee"]))
):
    create_audit_log(db, current_user.username, "FETCHED_RECORDS_LIST")
    query = db.query(DBRecord)

    # A. Search Functionality 
    if search:
        query = query.filter(DBRecord.title.ilike(f"%{search}%"))

    # B. Filtering Functionality
    if department:
        query = query.filter(DBRecord.department.ilike(department))

    # C. Sorting Functionality
    sort_field = getattr(DBRecord, sort_by, DBRecord.id)
    if order.lower() == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    offset = (page - 1) * size
    records = query.offset(offset).limit(size).all()
    return records

# 3. UPDATE (Admin & Manager only)
@router.put("/{record_id}", response_model=RecordResponse, summary=" Update record (Admin & Manager)")
def update_record(record_id: int, updated_data: RecordCreate, db: Session = Depends(get_db), current_user: UserResponse = Depends(verify_role(["Admin", "Manager"]))):
    db_record = db.query(DBRecord).filter(DBRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db_record.title = updated_data.title
    db_record.department = updated_data.department
    db.commit()
    db.refresh(db_record)
    
    create_audit_log(db, current_user.username, f"UPDATED_RECORD_ID_{record_id}")
    return db_record

# 4. DELETE (Admin only)
@router.delete("/{record_id}", status_code=status.HTTP_200_OK, summary="Delete record (Admin Only)")
def delete_record(record_id: int, db: Session = Depends(get_db), current_user: UserResponse = Depends(verify_role(["Admin"]))):
    db_record = db.query(DBRecord).filter(DBRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(db_record)
    db.commit()
    
    create_audit_log(db, current_user.username, f"DELETED_RECORD_ID_{record_id}")
    return {"message": "Record deleted successfully"}