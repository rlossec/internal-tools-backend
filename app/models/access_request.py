from datetime import datetime, timezone

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship

from app.db.database import Base

from .enum_types import RequestStatus


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)

    business_justification = Column(Text, nullable=False)
    status = Column(SqlEnum(RequestStatus), default=RequestStatus.pending)

    requested_at = Column(DateTime, default=datetime.now(timezone.utc))
    processed_at = Column(DateTime)
    processed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    processing_notes = Column(Text)
    
    # Relations
    user = relationship("User", back_populates="requests", foreign_keys=[user_id])
    tool = relationship("Tool", back_populates="requests", foreign_keys=[tool_id])
    processed_by_user = relationship("User", back_populates="processed_requests", foreign_keys=[processed_by])
