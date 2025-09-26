from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey, Integer, Text, String
from sqlalchemy.orm import relationship
from config.db import Base

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    message = Column(Text)
    created_at = Column(TIMESTAMP)

    session = relationship("Session", back_populates="chatlogs")