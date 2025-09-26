from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DocumentReferenceBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None

class DocumentReferenceCreate(DocumentReferenceBase):
    pass

class DocumentReferenceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None

class DocumentReference(DocumentReferenceBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True