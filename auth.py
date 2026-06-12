from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
import jwt
from datetime import datetime, timedelta, timezone
from app.core.security import get_password_hash, verify_password, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Authentication"])


fake_users_db = {}
user_id_counter = 1

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate):
    global user_id_counter
    if user_in.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    
    hashed_pword = get_password_hash(user_in.password)
    
    new_user = {
        "id": user_id_counter,
        "username": user_in.username,
        "email": user_in.email,
        "hashed_password": hashed_pword
    }
    fake_users_db[user_in.username] = new_user
    user_id_counter += 1
    return {"id": new_user["id"], "username": new_user["username"], "email": new_user["email"]}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode = {"sub": user["username"], "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}