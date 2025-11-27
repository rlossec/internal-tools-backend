from sqlalchemy import Column, Integer, String, Enum as SqlEnum, DateTime, Date
from sqlalchemy.orm import relationship

from app.db.database import Base
from .enum_types import DepartmentType, UserRole, UserStatus


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)

    department = Column(SqlEnum(DepartmentType), nullable=False)
    role = Column(SqlEnum(UserRole), default=UserRole.employee)
    status = Column(SqlEnum(UserStatus), default=UserStatus.active)

    hire_date = Column(Date, nullable=True)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # Relations
    accesses = relationship(
        "UserToolAccess",
        back_populates="user",
        primaryjoin="User.id == UserToolAccess.user_id"
    )
    requests = relationship(
        "AccessRequest",
        back_populates="user",
        primaryjoin="User.id == AccessRequest.user_id"
    )
    usages = relationship(
        "UsageLog",
        back_populates="user",
        primaryjoin="User.id == UsageLog.user_id"
    )
    granted_accesses = relationship(
        "UserToolAccess",
        back_populates="granted_by_user",
        primaryjoin="User.id == UserToolAccess.granted_by"
    )
    revoked_accesses = relationship(
        "UserToolAccess",
        back_populates="revoked_by_user",
        primaryjoin="User.id == UserToolAccess.revoked_by"
    )
    processed_requests = relationship(
        "AccessRequest",
        back_populates="processed_by_user",
        primaryjoin="User.id == AccessRequest.processed_by"
    )
