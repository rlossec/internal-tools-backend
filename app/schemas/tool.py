
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.schemas.common import SortOrder

# List Tools
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


# List tools filters and sorting
class FilterToolField(str, Enum):
    ID = "id"
    NAME = "name"
    VENDOR = "vendor"
    CATEGORY = "category"
    DEPARTMENT = "department"
    STATUS = "status"
    MAX_COST = "max_cost"
    MIN_COST = "min_cost"


class SortToolField(str, Enum):
    ID = "id"
    NAME = "name"
    MONTHLY_COST = "monthly_cost"
    CREATED_AT = "created_at"


class ToolFilters(BaseModel):
    """Schéma pour les filtres et le tri des outils."""
    category: Optional[str] = None
    vendor: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    max_cost: Optional[float] = None
    min_cost: Optional[float] = None
    sort_by: Optional[SortToolField] = None
    sort_order: Optional[SortOrder] = None
    
    @model_validator(mode='after')
    def validate_cost_range(self):
        """Valide que min_cost <= max_cost si les deux sont fournis."""
        if self.min_cost is not None and self.max_cost is not None:
            if self.min_cost > self.max_cost:
                raise ValueError("min_cost ne peut pas être supérieur à max_cost")
        return self
    
    def get_applied_filters(self) -> Dict[str, Any]:
        """Retourne un dictionnaire des filtres appliqués (non None)."""
        filters = {}
        if self.category is not None:
            filters["category"] = self.category
        if self.vendor is not None:
            filters["vendor"] = self.vendor
        if self.department is not None:
            filters["department"] = self.department
        if self.status is not None:
            filters["status"] = self.status
        if self.min_cost is not None:
            filters["min_cost"] = self.min_cost
        if self.max_cost is not None:
            filters["max_cost"] = self.max_cost
        if self.sort_by is not None:
            filters["sort_by"] = self.sort_by.value
        if self.sort_order is not None:
            filters["sort_order"] = self.sort_order
        return filters


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
