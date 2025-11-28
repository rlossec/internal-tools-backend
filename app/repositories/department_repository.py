"""Repository pour les données de département."""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import User, Tool, UserToolAccess
from app.models.enum_types import AccessStatus, UserStatus


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
                User.department,
                Tool.id.label('tool_id'),
                Tool.monthly_cost
            )
            .join(UserToolAccess, User.id == UserToolAccess.user_id)
            .join(Tool, UserToolAccess.tool_id == Tool.id)
            .filter(
                and_(
                    UserToolAccess.status == AccessStatus.active,
                    User.status == UserStatus.active
                )
            )
            .group_by(User.department, Tool.id, Tool.monthly_cost)
        )
        
        results = query.all()
        
        return [
            {
                'department': str(row.department.value),
                'tool_id': row.tool_id,
                'monthly_cost': float(row.monthly_cost)
            }
            for row in results
        ]
    
    def get_department_active_users_count(self) -> Dict[str, int]:
        """Récupère le nombre d'utilisateurs actifs par département."""
        query = (
            self._db.query(
                User.department,
                func.count(User.id).label('user_count')
            )
            .filter(User.status == UserStatus.active)
            .group_by(User.department)
        )
        
        results = query.all()
        
        return {
            str(row.department.value): row.user_count
            for row in results
        }

