"""Factory pour créer des CostTracking de test."""
from datetime import date
from typing import Optional

from tests.factories.base import BaseFactory
from app.models import CostTracking


class CostTrackingFactory(BaseFactory):
    """Factory pour créer des CostTracking de test."""
    
    def create(
        self,
        tool_id: int,
        month_year: Optional[date] = None,
        total_monthly_cost: float = 0.0,
        active_users_count: int = 0
    ) -> CostTracking:
        """
        Crée un CostTracking.
        
        Args:
            tool_id: ID de l'outil
            month_year: Mois/année (par défaut: premier jour du mois actuel)
            total_monthly_cost: Coût mensuel total
            active_users_count: Nombre d'utilisateurs actifs
        """
        if month_year is None:
            month_year = date.today().replace(day=1)
        
        return self._create(
            CostTracking,
            tool_id=tool_id,
            month_year=month_year,
            total_monthly_cost=total_monthly_cost,
            active_users_count=active_users_count
        )

