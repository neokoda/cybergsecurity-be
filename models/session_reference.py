from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey, Integer, Text, String
from sqlalchemy.orm import relationship
from config.db import Base


class SessionReference(Base):
    __tablename__ = "session_references"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    notes = Column(Text)
    validated_by = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    validated_at = Column(TIMESTAMP)

    session = relationship("Session", back_populates="references")