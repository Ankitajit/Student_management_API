from pydantic import BaseModel, Field
from datetime import datetime

CURRENT_YEAR = datetime.now().year 
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title cannot be empty")
    author: str = Field(..., min_length=1, description="Author name is required")
    category: str = Field(..., min_length=1, description="Category is required")
    published_year: int = Field(..., gt=0, le=CURRENT_YEAR, description="Published year cannot be in the future")
    available_copies: int = Field(..., ge=0, description="Available copies cannot be negative")

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    category: str
    published_year: int
    available_copies: int

    class Config:
        from_attributes = True