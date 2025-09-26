from enum import Enum
from pydantic import BaseModel, EmailStr

class UserRole(str, Enum):
    STAFF = "Staff"
    LAW = "Law"
    MANAGEMENT = "Management"
    ADMIN = "Admin"

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