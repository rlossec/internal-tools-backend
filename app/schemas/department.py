from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, field_validator


class SortDepartmentCostField(str, Enum):
    DEPARTMENT = "department"
    TOTAL_COST = "total_cost"


class DepartmentCostItem(BaseModel):
    department: str
    total_cost: float
    tools_count: int
    total_users: int
    average_cost_per_tool: float
    cost_percentage: float

    @field_validator('average_cost_per_tool', 'cost_percentage', 'total_cost')
    @classmethod
    def round_decimals(cls, v: float) -> float:
        return round(v, 2)


class DepartmentCostsSummary(BaseModel):
    total_company_cost: float
    departments_count: int
    most_expensive_department: str

    @field_validator('total_company_cost')
    @classmethod
    def round_decimals(cls, v: float) -> float:
        return round(v, 2)


class DepartmentCostsResponse(BaseModel):
    data: List[DepartmentCostItem]
    summary: DepartmentCostsSummary
