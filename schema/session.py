from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from schema.enums import RiskStatusEnum, StatusEnum


class SessionBase(BaseModel):
    contract_id: int
    current_version_id: Optional[int] = None
    summary: Optional[str] = None
    due_date: datetime 
    risk_status: Optional[RiskStatusEnum] = None
    status: Optional[StatusEnum] = StatusEnum.NEW

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    current_version_id: Optional[int] = None
    summary: Optional[str] = None
    due_date: datetime 
    risk_status: Optional[RiskStatusEnum] = None
    status: Optional[StatusEnum] = None

class Session(SessionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True