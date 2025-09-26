from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel


class ContractVersionBase(BaseModel):
    session_id: int
    file_path: str
    version_number: Optional[int] = None
    uploaded_by: UUID4

class ContractVersionCreate(ContractVersionBase):
    pass

class ContractVersion(ContractVersionBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True