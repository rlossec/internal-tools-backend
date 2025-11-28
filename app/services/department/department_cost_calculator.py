"""Calculateur pour les coûts par département."""
from typing import List, Dict, Any

from app.schemas import DepartmentCostItem


class DepartmentCostCalculator:
    """Calculateur pour les coûts par département."""
    
    @staticmethod
    def calculate_total_cost(
        department_costs_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calcule le coût total par département.
        """
        totals = {}
        for row in department_costs_data:
            dept = row['department']
            totals[dept] = totals.get(dept, 0.0) + row['monthly_cost']
        return totals
    
    @staticmethod
    def calculate_total_company_cost(
        department_totals: Dict[str, float]
    ) -> float:
        """
        Calcule le coût total de l'entreprise.
        """
        return sum(department_totals.values())
    
    @staticmethod
    def calculate_average_cost_per_tool(
        total_cost: float,
        tools_count: int
    ) -> float:
        """
        Calcule le coût moyen par outil.
        """
        return total_cost / tools_count if tools_count > 0 else 0.0
    
    @staticmethod
    def calculate_cost_percentage(
        department_cost: float,
        total_company_cost: float
    ) -> float:
        """
        Calcule le pourcentage du coût total.
        """
        return (department_cost / total_company_cost * 100) if total_company_cost > 0 else 0.0
    
    @staticmethod
    def find_most_expensive_department(
        department_items: List[DepartmentCostItem]
    ) -> str:
        """
        Trouve le département le plus cher.
        """
        if not department_items:
            return ""
        
        # Trier par total_cost DESC, puis par nom alphabétique ASC en cas d'égalité
        sorted_by_cost = sorted(
            department_items,
            key=lambda x: (-x.total_cost, x.department)
        )
        return sorted_by_cost[0].department

