
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.models import Category
from app.schemas.common import SortOrder
from app.models.enum_types import DepartmentType

# List Tools
class Tool(BaseModel): 
    id: int
    name: str
    description: Optional[str] = None
    vendor: str
    category: str
    monthly_cost: float
    owner_department: str
    status: str
    website_url: Optional[str] = None
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
    category: Optional[str] = None
    vendor: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    max_cost: Optional[float] = None
    min_cost: Optional[float] = None
    sort_by: Optional[SortToolField] = None
    sort_order: Optional[SortOrder] = None
    page: Optional[int] = None
    limit: Optional[int] = None
    
    @model_validator(mode='after')
    def validate_cost_range(self):
        """Valide que min_cost <= max_cost si les deux sont fournis."""
        if self.min_cost is not None and self.max_cost is not None:
            if self.min_cost > self.max_cost:
                raise ValueError("min_cost ne peut pas être supérieur à max_cost")
        return self
    
    @model_validator(mode='after')
    def validate_pagination(self):
        """Valide les paramètres de pagination."""
        if self.page is not None and self.page < 1:
            raise ValueError("page doit être supérieur ou égal à 1")
        if self.limit is not None and self.limit < 1:
            raise ValueError("limit doit être supérieur ou égal à 1")
        if self.limit is not None and self.limit > 100:
            raise ValueError("limit ne peut pas dépasser 100")
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
        if self.page is not None:
            filters["page"] = self.page
        if self.limit is not None:
            filters["limit"] = self.limit
        return filters


class PaginationInfo(BaseModel):
    """Métadonnées de pagination."""
    page: int
    limit: int
    total_pages: int
    total_items: int
    has_next: bool
    has_previous: bool


class ToolsListResponse(BaseModel):
    data: List[Tool]
    total: int
    filtered: int
    filters_applied: Dict[str, Any]
    pagination: Optional[PaginationInfo] = None


# Retrieve Tool
class SessionMetrics(BaseModel):
    total_sessions: int
    avg_session_minutes: int


class UsageMetrics(BaseModel):
    last_30_days: SessionMetrics


class ToolDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    vendor: str
    website_url: Optional[str] = None
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


# Create Tool
class ToolCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    vendor: str
    website_url: Optional[str] = None
    category_id: int
    monthly_cost: float
    owner_department: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Valide que le nom est est entre 2 et 100 caracteres."""
        if len(v) < 2 or len(v) > 100:
            raise ValueError("name doit avoir entre 2 et 100 caracteres")
        return v

    @field_validator('monthly_cost')
    @classmethod
    def validate_monthly_cost(cls, v):
        """Valide que le coût mensuel est positif et avec maximum 2 decimales."""
        if v < 0:
            raise ValueError("monthly_cost doit être supérieur ou égal à 0")
        # Vérifier le nombre de décimales en multipliant par 100 et vérifiant si c'est un entier
        if abs(v * 100 - round(v * 100)) > 1e-10:
            raise ValueError("monthly_cost doit avoir maximum 2 decimales")
        return v
    
    @field_validator('owner_department')
    @classmethod
    def validate_department(cls, v):
        """Valide que le département est valide."""
        try:
            DepartmentType(v)
        except ValueError:
            raise ValueError(f"owner_department doit être l'un de: {', '.join([d.value for d in DepartmentType])}")
        return v
    
    @field_validator('website_url')
    @classmethod
    def validate_website_url(cls, v):
        """Valide que l'URL du site web est valide."""
        if v is None:
            return v
        if not v.startswith('http://') and not v.startswith('https://'):
            raise ValueError("website_url doit commencer par http:// ou https://")
        return v

    @field_validator('category_id')
    @classmethod
    def validate_category_id(cls, v):
        """Valide que category_id est un entier positif."""
        if v is None:
            return v
        if not isinstance(v, int) or v <= 0:
            raise ValueError("category_id doit être un entier positif")
        return v

    @field_validator('vendor')
    @classmethod
    def validate_vendor(cls, v):
        """Valide que le vendor est entre 2 et 100 caracteres."""
        if v is None:
            return v
        if len(v) < 2 or len(v) > 100:
            raise ValueError("vendor doit avoir entre 2 et 100 caracteres")
        return v


class ToolCreateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    vendor: str
    website_url: Optional[str] = None
    category: str
    monthly_cost: float
    owner_department: str
    status: str
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


# Update Tool
class ToolUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    website_url: Optional[str] = None
    category_id: Optional[int] = None
    monthly_cost: Optional[float] = None
    owner_department: Optional[str] = None
    status: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Valide que le nom est entre 2 et 100 caracteres."""
        if v is None:
            return v
        if len(v) < 2 or len(v) > 100:
            raise ValueError("name doit avoir entre 2 et 100 caracteres")
        return v
    
    @field_validator('monthly_cost')
    @classmethod
    def validate_monthly_cost(cls, v):
        """Valide que le coût mensuel est positif et avec maximum 2 decimales."""
        if v is None:
            return v
        if v < 0:
            raise ValueError("monthly_cost doit être supérieur ou égal à 0")
        # Vérifier le nombre de décimales en multipliant par 100 et vérifiant si c'est un entier
        if abs(v * 100 - round(v * 100)) > 1e-10:
            raise ValueError("monthly_cost doit avoir maximum 2 decimales")
        return v
    
    @field_validator('owner_department')
    @classmethod
    def validate_department(cls, v):
        """Valide que le département est valide."""
        if v is None:
            return v
        try:
            DepartmentType(v)
        except ValueError:
            raise ValueError(f"owner_department doit être l'un de: {', '.join([d.value for d in DepartmentType])}")
        return v
    
    @field_validator('website_url')
    @classmethod
    def validate_website_url(cls, v):
        """Valide que l'URL du site web est valide."""
        if v is None:
            return v
        if not v.startswith('http://') and not v.startswith('https://'):
            raise ValueError("website_url doit commencer par http:// ou https://")
        return v
    
    @field_validator('category_id')
    @classmethod
    def validate_category_id(cls, v):
        """Valide que category_id est un entier positif."""
        if v is None:
            return v
        if not isinstance(v, int) or v <= 0:
            raise ValueError("category_id doit être un entier positif")
        return v
    
    @field_validator('vendor')
    @classmethod
    def validate_vendor(cls, v):
        """Valide que le vendor est entre 2 et 100 caracteres."""
        if v is None:
            return v
        if len(v) < 2 or len(v) > 100:
            raise ValueError("vendor doit avoir entre 2 et 100 caracteres")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Valide que le statut est valide."""
        if v is None:
            return v
        from app.models.enum_types import ToolStatus
        try:
            ToolStatus(v)
        except ValueError:
            raise ValueError(f"status doit être l'un de: {', '.join([s.value for s in ToolStatus])}")
        return v


class ToolUpdateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    vendor: str
    website_url: Optional[str] = None
    category: str
    monthly_cost: float
    owner_department: str
    status: str
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

