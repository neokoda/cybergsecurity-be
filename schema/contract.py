from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel
from enums import JenisKontrakEnum

class ContractBase(BaseModel):
    title: str
    description: Optional[str] = None
    jenis_kontrak: Optional[JenisKontrakEnum] = None

class ContractCreate(ContractBase):
    created_by: UUID4

class ContractUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    jenis_kontrak: Optional[JenisKontrakEnum] = None

class Contract(ContractBase):
    id: int
    created_by: UUID4
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True