from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import user as user_model
from schema import user as user_schema
from utils.db import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register", response_model=user_schema.UserOut)
def register_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    hashed_password = "hashed_password_here"
    
    new_user = user_model.User(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user