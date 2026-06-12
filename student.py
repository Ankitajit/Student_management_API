from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name cannot be empty")
    age: int = Field(..., gt=18, description="Age must be greater than 18")
    email: EmailStr
    course: str = Field(..., min_length=1)

class StudentResponse(BaseModel):
    id: int
    name: str
    age: int
    email: str
    course: str

    class Config:
        from_attributes = True