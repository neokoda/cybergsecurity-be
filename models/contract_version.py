from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from config.db import Base

class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    file_path = Column(String, nullable=False)
    version_number = Column(Integer)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    created_at = Column(TIMESTAMP)

    #session = relationship("Session", back_populates="versions")