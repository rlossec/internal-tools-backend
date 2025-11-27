from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DECIMAL, Enum as SqlEnum, DateTime
)
from sqlalchemy.orm import relationship

from app.db.database import Base

from .enum_types import DepartmentType, ToolStatus


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    vendor = Column(String(100))
    website_url = Column(String(255))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    monthly_cost = Column(DECIMAL(10, 2), nullable=False)
    active_users_count = Column(Integer, nullable=False, default=0)
    owner_department = Column(SqlEnum(DepartmentType), nullable=False)
    status = Column(SqlEnum(ToolStatus), default=ToolStatus.active)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relations
    category = relationship("Category", back_populates="tools")
    accesses = relationship("UserToolAccess", back_populates="tool")
    requests = relationship("AccessRequest", back_populates="tool")
    usages = relationship("UsageLog", back_populates="tool")
    costs = relationship("CostTracking", back_populates="tool")
