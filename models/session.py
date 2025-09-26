import enum
from sqlalchemy import TIMESTAMP, Column, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from config.db import Base
from .enums import RiskStatusEnum, StatusEnum



class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    current_version_id = Column(Integer, ForeignKey("contract_versions.id"))
    summary = Column(Text)
    risk_status = Column(Enum(RiskStatusEnum))
    status = Column(Enum(StatusEnum))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    contract = relationship("Contract", back_populates="sessions")
    #versions = relationship("ContractVersion", back_populates="session")
    comments = relationship("Comment", back_populates="session")
    chatlogs = relationship("ChatLog", back_populates="session")
    references = relationship("SessionReference", back_populates="session")