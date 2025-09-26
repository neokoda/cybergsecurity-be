from sqlalchemy import TIMESTAMP, Column, Integer, String, Text
from sqlalchemy.orm import relationship
from config.db import Base

class DocumentReference(Base):
    __tablename__ = "document_references"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    file_path = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)