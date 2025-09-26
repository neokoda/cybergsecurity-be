from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel


class CommentBase(BaseModel):
    session_id: int
    user_id: UUID4
    comment: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True