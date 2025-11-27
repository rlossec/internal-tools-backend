from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base

from .enum_types import DEFAULT_COLOR_HEX


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    color_hex = Column(String(7), default=DEFAULT_COLOR_HEX)
    created_at = Column(DateTime)

    # Relation avec Tool
    tools = relationship("Tool", back_populates="category")

