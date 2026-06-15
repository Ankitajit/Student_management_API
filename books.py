from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.book import BookModel
from app.schemas.book import BookCreate, BookResponse

router = APIRouter(prefix="/books", tags=["Library Books"])

# ADD BOOK
@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED, summary="Add a new book")
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = BookModel(
        title=book.title,
        author=book.author,
        category=book.category,
        published_year=book.published_year,
        available_copies=book.available_copies
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

# GET ALL BOOKS 
@router.get("/", response_model=List[BookResponse], summary="Get all books")
def get_all_books(db: Session = Depends(get_db)):
    return db.query(BookModel).all()

# GET BOOK BY ID 
@router.get("/{book_id}", response_model=BookResponse, summary="Get book by ID")
def get_book_by_id(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# UPDATE BOOK DETAILS
@router.put("/{book_id}", response_model=BookResponse, summary="Update book details")
def update_book(book_id: int, updated_book: BookCreate, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book.title = updated_book.title
    book.author = updated_book.author
    book.category = updated_book.category
    book.published_year = updated_book.published_year
    book.available_copies = updated_book.available_copies
    
    db.commit()
    db.refresh(book)
    return book

# DELETE BOOK
@router.delete("/{book_id}", summary="Delete a book")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(book)
    db.commit()
    return {"detail": f"Book with ID {book_id} successfully deleted"}