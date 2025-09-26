from sqlalchemy import TIMESTAMP, UUID, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from config.db import Base
from .enums import JenisKontrakEnum

    
class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    jenis_kontrak = Column(Enum(JenisKontrakEnum))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    creator = relationship("User", back_populates="contracts")
    sessions = relationship("Session", back_populates="contract")
    workflows = relationship("Workflow", back_populates="contract")