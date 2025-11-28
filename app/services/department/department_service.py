"""Service pour la logique métier des départements."""
from typing import Optional

from app.repositories import DepartmentRepository
from app.schemas import (
    DepartmentCostsResponse,
    SortDepartmentCostField,
    SortOrder
)
from app.services.department.department_cost_calculator import DepartmentCostCalculator
from app.services.department.department_cost_aggregator import DepartmentCostAggregator


class DepartmentService:
    """Service pour la logique métier des départements."""
    
    def __init__(
        self,
        department_repository: DepartmentRepository,
        calculator: Optional[DepartmentCostCalculator] = None,
        aggregator: Optional[DepartmentCostAggregator] = None
    ):
        """
        Initialise le service pour les départements.
        
        Args:
            department_repository: Repository pour les données de département
            calculator: Calculateur de coûts (optionnel, crée une instance par défaut)
            aggregator: Agrégateur de coûts (optionnel, crée une instance par défaut)
        """
        self._repository = department_repository
        self._calculator = calculator or DepartmentCostCalculator()
        self._aggregator = aggregator or DepartmentCostAggregator(self._calculator)
    
    def _sort_department_items(
        self,
        department_items: list,
        sort_by: SortDepartmentCostField,
        order: SortOrder
    ) -> None:
        """Trie les items de département."""
        reverse = (order == SortOrder.DESC)
        if sort_by == SortDepartmentCostField.TOTAL_COST:
            department_items.sort(key=lambda x: x.total_cost, reverse=reverse)
        elif sort_by == SortDepartmentCostField.DEPARTMENT:
            department_items.sort(key=lambda x: x.department, reverse=reverse)
    
    def get_department_costs(
        self,
        sort_by: SortDepartmentCostField = SortDepartmentCostField.TOTAL_COST,
        order: SortOrder = SortOrder.DESC
    ) -> DepartmentCostsResponse:
        """
        Récupère la répartition des coûts par département.
        
        Args:
            sort_by: Champ de tri (department ou total_cost)
            order: Ordre de tri (asc ou desc)
            
        Returns:
            DepartmentCostsResponse avec les données et le résumé
        """
        # Récupérer les données brutes
        department_costs_data = self._repository.get_department_costs_data()
        department_users_count = self._repository.get_department_active_users_count()
        
        # Agrégation par département
        department_aggregates = self._aggregator.aggregate_costs(
            department_costs_data,
            department_users_count
        )
        
        # Calculer le coût total de l'entreprise
        department_totals = self._calculator.calculate_total_cost(department_costs_data)
        total_company_cost = self._calculator.calculate_total_company_cost(department_totals)
        
        # Construire les items de département
        department_items = self._aggregator.build_department_items(
            department_aggregates,
            total_company_cost
        )
        
        # Gérer les départements sans outils actifs
        self._aggregator.add_departments_without_tools(
            department_items,
            department_users_count,
            department_aggregates
        )
        
        # Trier les résultats
        self._sort_department_items(department_items, sort_by, order)
        
        # Construire le résumé
        summary = self._aggregator.build_summary(
            department_items,
            total_company_cost
        )
        
        return DepartmentCostsResponse(
            data=department_items,
            summary=summary
        )

