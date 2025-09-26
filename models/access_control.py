from sqlalchemy import Column, ForeignKey, Integer, String
from config.db import Base

class AccessControl(Base):
    __tablename__ = "access_control"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    workflow_step = Column(String)  
    permission = Column(String)