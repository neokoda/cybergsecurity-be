from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel
from document_reference import DocumentReference


class SessionReferenceBase(BaseModel):
    session_id: int
    reference_id: int
    notes: Optional[str] = None
    validated_by: UUID4

class SessionReferenceCreate(SessionReferenceBase):
    pass

class SessionReference(SessionReferenceBase):
    id: int
    validated_at: Optional[datetime] = None
    reference: Optional[DocumentReference] = None

    class Config:
        from_attributes = True