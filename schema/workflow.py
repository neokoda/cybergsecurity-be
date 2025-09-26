from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel
from enums import StatusEnum

class WorkflowBase(BaseModel):
    contract_id: int
    step: str
    assigned_to: UUID4
    status: Optional[StatusEnum] = StatusEnum.NEW
    notes: Optional[str] = None

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(BaseModel):
    step: Optional[str] = None
    assigned_to: Optional[UUID4] = None
    status: Optional[StatusEnum] = None
    notes: Optional[str] = None

class Workflow(WorkflowBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True