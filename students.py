from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List


from app.core.database import get_db, SessionLocal
from app.models.student import StudentModel
from app.schemas.student import StudentCreate, StudentResponse  

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



#search, filter, sort, pagination endpoints
@router.get("/search", response_model=List[StudentResponse])
def search_students(q: str, db: Session = Depends(get_db)):
    return db.query(StudentModel).filter(
        (StudentModel.name.contains(q)) | (StudentModel.email.contains(q))
    ).all()

@router.get("/filter", response_model=List[StudentResponse])
def filter_students(
    course: str | None = None, 
    age: int | None = None, 
    db: Session = Depends(get_db)
):
    query = db.query(StudentModel)
    if course:
        query = query.filter(StudentModel.course == course)
    if age:
        query = query.filter(StudentModel.age == age)
    return query.all()

@router.get("/sort", response_model=List[StudentResponse])
def sort_students(
    sortBy: str = Query("name", description="Sort by 'name' or 'age'"), 
    order: str = Query("asc", description="Order 'asc' or 'desc'"),
    db: Session = Depends(get_db)
    ):

    if sortBy not in ["name", "age"]:
        raise HTTPException(status_code=400, detail="Invalid sortBy value")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order value")

    query = db.query(StudentModel)
 
    if order.lower() == "desc":
        query = query.order_by(getattr(StudentModel, sortBy).desc())
    else:
        query = query.order_by(getattr(StudentModel, sortBy).asc())

    results = query.all()    
    return results

@router.get("/page", response_model=List[StudentResponse])
def paginate_students(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    return db.query(StudentModel).offset(offset).limit(limit).all()




# CREATE
@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = StudentModel(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# Get All Students
@router.get("/", response_model=List[StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    return db.query(StudentModel).all()

# Get Student By ID
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

#  UPDATE 
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, updated_student: StudentCreate, db: Session = Depends(get_db)):
    student_query = db.query(StudentModel).filter(StudentModel.id == student_id)
    student = student_query.first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_query.update(updated_student.dict(), synchronize_session=False)
    db.commit()
    return student_query.first()

#  DELETE 
@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student_query = db.query(StudentModel).filter(StudentModel.id == student_id)
    student = student_query.first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_query.delete(synchronize_session=False)
    db.commit()
    return {"message": "Student deleted successfully"}