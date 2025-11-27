from datetime import datetime, timezone

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SqlEnum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base
from .enum_types import AccessStatus


class UserToolAccess(Base):
    __tablename__ = "user_tool_access"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    granted_at = Column(DateTime, default=datetime.now(timezone.utc))
    granted_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    revoked_at = Column(DateTime)
    revoked_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    status = Column(SqlEnum(AccessStatus), default=AccessStatus.active)
    
    __table_args__ = (
        UniqueConstraint("user_id", "tool_id", "status"),
    )

    # Relations
    user = relationship("User", back_populates="accesses", foreign_keys=[user_id])
    tool = relationship("Tool", back_populates="accesses", foreign_keys=[tool_id])
    granted_by_user = relationship("User", back_populates="granted_accesses", foreign_keys=[granted_by])
    revoked_by_user = relationship("User", back_populates="revoked_accesses", foreign_keys=[revoked_by])
    

