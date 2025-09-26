import enum
from sqlalchemy import TIMESTAMP, UUID, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from config.db import Base

class StatusEnum(str, enum.Enum):
    NEW = "NEW"
    ON_VERIFICATION = "ON_VERIFICATION"
    ON_REVIEW = "ON_REVIEW"
    ACCEPTED = "ACCEPTED"
    CONFLICT = "CONFLICT"

class Workflow(Base):
    __tablename__ = "workflow"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    step = Column(String)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    status = Column(Enum(StatusEnum))
    notes = Column(Text)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    contract = relationship("Contract", back_populates="workflows")