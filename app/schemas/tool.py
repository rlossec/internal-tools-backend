
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, field_validator


class Tool(BaseModel): 
    id: int
    name: str
    description: str
    vendor: str
    category: str
    monthly_cost: float
    owner_department: str
    status: str
    website_url: str
    active_users_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('category', mode='before')
    @classmethod
    def transform_category(cls, v):
        """Transforme l'objet Category en string (nom de la catégorie)."""
        if v is None:
            return ""
        if hasattr(v, 'name'):
            return v.name
        return str(v) if v else ""


class ToolsListResponse(BaseModel):
    data: List[Tool]
    total: int
    filtered: int
    filters_applied: Dict[str, Any]


# Retrieve Tool
class SessionMetrics(BaseModel):
    total_sessions: int
    avg_session_minutes: int


class UsageMetrics(BaseModel):
    last_30_days: SessionMetrics


class ToolDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    vendor: str
    website_url: str
    category: str
    monthly_cost: float
    owner_department: str
    status: str
    active_users_count: int
    total_monthly_cost: float
    created_at: datetime
    updated_at: datetime
    usage_metrics: UsageMetrics
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('category', mode='before')
    @classmethod
    def transform_category(cls, v):
        """Transforme l'objet Category en string (nom de la catégorie)."""
        if v is None:
            return ""
        if hasattr(v, 'name'):
            return v.name
        return str(v) if v else ""
