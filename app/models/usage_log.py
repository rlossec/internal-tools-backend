from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship

from app.db.database import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    session_date = Column(Date, nullable=False)
    usage_minutes = Column(Integer, default=0)
    actions_count = Column(Integer, default=0)
    created_at = Column(DateTime)

    # Relations
    user = relationship("User", back_populates="usages", foreign_keys=[user_id])
    tool = relationship("Tool", back_populates="usages", foreign_keys=[tool_id])
    