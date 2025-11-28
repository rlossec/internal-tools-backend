"""Services pour les départements."""
from .department_service import DepartmentService
from .department_cost_calculator import DepartmentCostCalculator
from .department_cost_aggregator import DepartmentCostAggregator

__all__ = [
    "DepartmentService",
    "DepartmentCostCalculator",
    "DepartmentCostAggregator",
]

