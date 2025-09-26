from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel
from schema.enums import JenisKontrakEnum

class ContractBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_path: str
    jenis_kontrak: Optional[JenisKontrakEnum] = None

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None
    jenis_kontrak: Optional[JenisKontrakEnum] = None

class Contract(ContractBase):
    id: int
    created_by: UUID4
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True