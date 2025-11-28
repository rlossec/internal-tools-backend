"""Repository pour les données de département."""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models import Tool, CostTracking
from app.models.enum_types import ToolStatus


class DepartmentRepository:
    """Repository pour les requêtes liées aux départements."""
    
    def __init__(self, session: Session):
        self._db = session
    
    def get_department_costs_data(self) -> List[Dict[str, Any]]:
        """
        Récupère les données brutes pour le calcul des coûts par département.
        """
        
        query = (
            self._db.query(
                Tool.owner_department,
                Tool.id.label('tool_id'),
                CostTracking.total_monthly_cost.label('monthly_cost'),
                CostTracking.active_users_count.label('active_users_count')
            )
            .join(CostTracking, Tool.id == CostTracking.tool_id)
            .filter(Tool.status == ToolStatus.active)
        )
        
        results = query.all()
        
        return [
            {
                'department': str(row.owner_department.value),
                'tool_id': row.tool_id,
                'monthly_cost': float(row.monthly_cost),
                'active_users_count': int(row.active_users_count)
            }
            for row in results
        ]

