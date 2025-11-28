"""Agrégateur de données de coûts par département."""
from typing import List, Dict, Any
from collections import defaultdict

from app.schemas import DepartmentCostItem, DepartmentCostsSummary
from app.services.department.department_cost_calculator import DepartmentCostCalculator


class DepartmentCostAggregator:
    """Agrégateur de données de coûts par département."""
    
    def __init__(self, calculator: DepartmentCostCalculator = None):
        """Initialise l'agrégateur avec un calculateur optionnel."""
        self._calculator = calculator or DepartmentCostCalculator()
    
    def aggregate_costs(
        self,
        department_costs_data: List[Dict[str, Any]],
        department_users_count: Dict[str, int]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Agrège les données de coûts par département.
        """
        department_aggregates: Dict[str, Dict] = defaultdict(lambda: {
            'total_cost': 0.0,
            'tools': set(),  # Set pour éviter les doublons d'outils
            'total_users': 0
        })
        
        # Calculer les coûts totaux par département
        for row in department_costs_data:
            dept = row['department']
            department_aggregates[dept]['total_cost'] += row['monthly_cost']
            department_aggregates[dept]['tools'].add(row['tool_id'])
        
        # Ajouter le nombre d'utilisateurs par département
        for dept, user_count in department_users_count.items():
            if dept in department_aggregates:
                department_aggregates[dept]['total_users'] = user_count
        
        return department_aggregates
    
    def build_department_items(
        self,
        department_aggregates: Dict[str, Dict[str, Any]],
        total_company_cost: float
    ) -> List[DepartmentCostItem]:
        """
        Construit les items de département à partir des agrégats.
        """
        department_items: List[DepartmentCostItem] = []
        
        for dept, agg in department_aggregates.items():
            tools_count = len(agg['tools'])
            
            # Calculer la moyenne par outil
            average_cost_per_tool = self._calculator.calculate_average_cost_per_tool(
                agg['total_cost'],
                tools_count
            )
            
            # Calculer le pourcentage
            cost_percentage = self._calculator.calculate_cost_percentage(
                agg['total_cost'],
                total_company_cost
            )
            
            department_items.append(
                DepartmentCostItem(
                    department=dept,
                    total_cost=round(agg['total_cost'], 2),
                    tools_count=tools_count,
                    total_users=agg['total_users'],
                    average_cost_per_tool=average_cost_per_tool,
                    cost_percentage=cost_percentage
                )
            )
        
        return department_items
    
    def add_departments_without_tools(
        self,
        department_items: List[DepartmentCostItem],
        department_users_count: Dict[str, int],
        department_aggregates: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Ajoute les départements sans outils actifs.
        """
        for dept, user_count in department_users_count.items():
            if dept not in department_aggregates:
                department_items.append(
                    DepartmentCostItem(
                        department=dept,
                        total_cost=0.0,
                        tools_count=0,
                        total_users=user_count,
                        average_cost_per_tool=0.0,
                        cost_percentage=0.0
                    )
                )
    
    def build_summary(
        self,
        department_items: List[DepartmentCostItem],
        total_company_cost: float
    ) -> DepartmentCostsSummary:
        """
        Construit le résumé des coûts.
        """
        most_expensive_department = self._calculator.find_most_expensive_department(
            department_items
        )
        
        return DepartmentCostsSummary(
            total_company_cost=total_company_cost,
            departments_count=len(department_items),
            most_expensive_department=most_expensive_department
        )

