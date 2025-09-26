from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from models import user as user_model
from schema import auth as auth_schema
from schema.token import Token
from utils.db import get_db
from utils.auth import AuthHandler, JWTBearerWithRole

auth_handler = AuthHandler()
    
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user: auth_schema.UserCreate, db: Session = Depends(get_db), current_user=Depends(JWTBearerWithRole(roles=["admin"]))):
    existing_user = db.query(user_model.User).filter(user_model.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    hashed_password = auth_handler.get_password_hash(user.password)
    now = datetime.now(timezone.utc)

    new_user = user_model.User(
        name=user.full_name, 
        email=user.email,
        password=hashed_password,
        role=user.role,
        created_at=now,
        updated_at=now
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token_expires = timedelta(minutes=60)
    access_token = auth_handler.create_access_token(
        data={"email": new_user.email, "role": new_user.role}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_user(user_data: auth_schema.UserLogin, db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter(user_model.User.email == user_data.email).first()

    if user is None or not auth_handler.verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # update last login timestamp
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    access_token_expires = timedelta(minutes=60)
    access_token = auth_handler.create_access_token(
        data={"email": user.email, "role": user.role}, 
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
