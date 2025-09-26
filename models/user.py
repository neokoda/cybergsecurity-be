import uuid
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from config.db import Base

class User(Base):
    __tablename__ = "users"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    role = relationship("Role", back_populates="users")
    contracts = relationship("Contract", back_populates="creator")
