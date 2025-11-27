

from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class CostTracking(Base):
    __tablename__ = "cost_tracking"

    id = Column(Integer, primary_key=True)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="CASCADE"), nullable=False)
    month_year = Column(Date, nullable=False)
    total_monthly_cost = Column(DECIMAL(10, 2), nullable=False)
    active_users_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("tool_id", "month_year"),
    )

    # Relations
    tool = relationship("Tool", back_populates="costs", foreign_keys=[tool_id])
