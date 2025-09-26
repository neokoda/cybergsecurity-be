from sqlalchemy import Column, Integer, String
from config.db import Base

class User(Base):
    __tablename__ = "users"
    UserID = Column(Integer, primary_key=True, index=True)
    Email = Column(String, unique=True, index=True)
    Password = Column(String)
    FullName = Column(String)
    Role = Column(String)