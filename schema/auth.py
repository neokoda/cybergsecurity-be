from enum import Enum
from pydantic import BaseModel, EmailStr

class UserRole(str, Enum):
    STAFF = "user"
    LAW = "reviewer"
    MANAGEMENT = "manager"
    ADMIN = "admin"

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True