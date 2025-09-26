from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel


class ChatLogBase(BaseModel):
    session_id: int
    user_id: UUID4
    message: str

class ChatLogCreate(ChatLogBase):
    pass

class ChatLog(ChatLogBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True