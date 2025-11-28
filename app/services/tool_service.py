from datetime import datetime, timedelta
import math
from typing import Optional

from app.repositories import ToolRepository
from app.schemas import (
    Tool, ToolFilters, ToolsListResponse, NoResultsFoundResponse, PaginationInfo, 
    ToolDetailResponse, UsageMetrics, SessionMetrics, 
    ToolCreateRequest, ToolCreateResponse, ToolUpdateRequest, ToolUpdateResponse,
    ExpensiveToolItem, ExpensiveToolsAnalysis, ExpensiveToolsResponse, EfficiencyRating,
    SortToolField, SortOrder
)
from app.models.enum_types import DepartmentType, ToolStatus
from app.core.errors import ToolNotFoundError


class ToolService:
    """Service pour la logique métier des outils."""
    
    def __init__(self, tool_repository: ToolRepository):
        self._repository = tool_repository
    
    def create_tool(self, tool_data: ToolCreateRequest) -> ToolCreateResponse:
        """Crée un nouvel outil."""
        
        department = DepartmentType(tool_data.owner_department)

        tool_model = self._repository.create_tool(
            name=tool_data.name,
            description=tool_data.description,
            vendor=tool_data.vendor,
            website_url=tool_data.website_url,
            category_id=tool_data.category_id,
            monthly_cost=tool_data.monthly_cost,
            owner_department=department,
        )
        return ToolCreateResponse.model_validate(tool_model)
    
    def update_tool(self, tool_id: int, tool_data: ToolUpdateRequest) -> ToolUpdateResponse:
        """Met à jour un outil existant."""
        # Récupérer les champs explicitement fournis (exclure ceux non fournis)
        provided_fields = tool_data.model_dump(exclude_unset=True)
        
        # Convertir enums si fournis
        owner_department_enum = ...
        if "owner_department" in provided_fields:
            if provided_fields["owner_department"] is not None:
                owner_department_enum = DepartmentType(provided_fields["owner_department"])
            else:
                owner_department_enum = None  # Explicitement fourni comme None
        
        status_enum = ...
        if "status" in provided_fields:
            if provided_fields["status"] is not None:
                status_enum = ToolStatus(provided_fields["status"])
            else:
                status_enum = None  # Explicitement fourni comme None
        
        # Préparer les paramètres pour le repository
        name = provided_fields.get("name", ...) if "name" in provided_fields else ...
        description = provided_fields.get("description", ...) if "description" in provided_fields else ...
        vendor = provided_fields.get("vendor", ...) if "vendor" in provided_fields else ...
        website_url = provided_fields.get("website_url", ...) if "website_url" in provided_fields else ...
        category_id = provided_fields.get("category_id", ...) if "category_id" in provided_fields else ...
        monthly_cost = provided_fields.get("monthly_cost", ...) if "monthly_cost" in provided_fields else ...
        
        # Mettre à jour via le repository
        tool_model = self._repository.update_tool(
            tool_id=tool_id,
            name=name,
            description=description,
            vendor=vendor,
            website_url=website_url,
            category_id=category_id,
            monthly_cost=monthly_cost,
            owner_department=owner_department_enum,
            status=status_enum,
        )
        
        # Convertir en ToolUpdateResponse
        return ToolUpdateResponse.model_validate(tool_model)
    
    def get_tool(self, tool_id: int) -> ToolDetailResponse:
        """Récupère un outil par son ID."""
        tool_model = self._repository.get_tool(tool_id)
        
        if not tool_model:
            raise ToolNotFoundError(tool_id)

        tool = Tool.model_validate(tool_model)
        
        # Calcul des métriques d'utilisation (30 derniers jours)
        usage_metrics = self.get_tool_usage_metrics_last_days(tool_id, days_number=30)
        
        # Calcul du coût total mensuel
        total_monthly_cost = self.get_tool_total_monthly_cost(tool_id)
        
        return ToolDetailResponse(
            **tool.model_dump(),
            total_monthly_cost=total_monthly_cost,
            usage_metrics=usage_metrics
        )
    
    def list_tools(self, filters: ToolFilters) -> ToolsListResponse | NoResultsFoundResponse:
        """
        Liste les outils avec filtres, tri et pagination.
        """
        tool_models = self._repository.list_tools(filters)
        tools = [Tool.model_validate(tool) for tool in tool_models]
        
        if not tools:
            return NoResultsFoundResponse()
            
        total = self._repository.count_all()
        filtered_total = self._repository.count_filtered(filters)
        
        # Calcul des métadonnées de pagination
        pagination = None
        if filters.page is not None and filters.limit is not None:
            total_pages = math.ceil(filtered_total / filters.limit) if filtered_total > 0 else 0
            pagination = PaginationInfo(
                page=filters.page,
                limit=filters.limit,
                total_pages=total_pages,
                total_items=filtered_total,
                has_next=filters.page < total_pages,
                has_previous=filters.page > 1
            )
        
        return ToolsListResponse(
            data=tools,
            total=total,
            filtered=filtered_total,
            filters_applied=filters.get_applied_filters(),
            pagination=pagination
        )

    def get_tool_total_monthly_cost(self, tool_id: int) -> float:
        """
        Calcule le coût total mensuel d'un outil.
        
        Formule : monthly_cost * active_users_count
        """
        tool = self._repository.get_tool(tool_id)
        if not tool:
            raise ToolNotFoundError(tool_id)

        total_monthly_cost = float(tool.monthly_cost) * tool.active_users_count
        
        return total_monthly_cost
    
    def get_tool_usage_metrics_last_days(self, tool_id: int, days_number: int) -> UsageMetrics:
        """
        Récupère les métriques d'utilisation d'un outil pour les N derniers jours.
        """
        tool = self._repository.get_tool(tool_id)
        if not tool:
            raise ToolNotFoundError(tool_id)

        usage_logs = self._repository.get_tool_usage_logs(tool_id)
        # Filtrer les logs des N derniers jours
        # FAKE_DATE = date(2025, 6, 1) pour les tests
        cutoff_date = datetime.now().date() - timedelta(days=days_number)
        filtered_logs = [
            log for log in usage_logs 
            if log.session_date >= cutoff_date
        ]
        total_sessions = len(filtered_logs)
        total_minutes = sum(log.usage_minutes for log in filtered_logs)
        
        # Éviter la division par zéro
        avg_session_minutes = total_minutes / total_sessions if total_sessions > 0 else 0
        
        return UsageMetrics(
            last_30_days=SessionMetrics(
                total_sessions=total_sessions,
                avg_session_minutes=int(avg_session_minutes)
            )
        )

    def get_expensive_tools(
        self, 
        min_cost: Optional[float] = None, 
        limit: Optional[int] = None
    ) -> ExpensiveToolsResponse:
        """
        Récupère les outils les plus coûteux avec analyse d'efficacité.
        
        Args:
            min_cost: Coût minimum pour filtrer les outils
            limit: Nombre maximum d'outils à retourner
            
        Returns:
            ExpensiveToolsResponse: Réponse avec les outils et l'analyse
        """
        # Construire les filtres pour récupérer les outils
        filters = ToolFilters(
            min_cost=min_cost,
            sort_by=SortToolField.MONTHLY_COST,
            sort_order=SortOrder.DESC,
            limit=limit
        )
        
        # Récupérer tous les outils (sans pagination pour l'analyse)
        all_tools = self._repository.list_tools(
            ToolFilters(
                min_cost=min_cost,
                sort_by=SortToolField.MONTHLY_COST,
                sort_order=SortOrder.DESC
            )
        )
        
        # Récupérer les outils limités pour la réponse
        limited_tools = self._repository.list_tools(filters)
        
        # Calculer les statistiques globales de l'entreprise
        total_monthly_cost, total_active_users = self._repository.get_company_cost_statistics()
        
        # Calculer avg_cost_per_user_company (moyenne pondérée globale)
        # Exclut les outils à 0 utilisateurs (déjà fait dans get_company_cost_statistics)
        avg_cost_per_user_company = (
            total_monthly_cost / total_active_users 
            if total_active_users > 0 else 0.0
        )
        
        # Calculer cost_per_user et efficiency_rating pour chaque outil limité
        expensive_tool_items = []
        
        for tool_model in limited_tools:
            # Calculer cost_per_user avec gestion de la division par zéro
            cost_per_user = (
                float(tool_model.monthly_cost) / tool_model.active_users_count
                if tool_model.active_users_count > 0 else 0.0
            )
            
            # Calculer efficiency_rating basé sur la comparaison avec la moyenne
            efficiency_rating = self._calculate_efficiency_rating(
                cost_per_user, 
                avg_cost_per_user_company
            )
            
            expensive_tool_items.append(
                ExpensiveToolItem(
                    id=tool_model.id,
                    name=tool_model.name,
                    monthly_cost=float(tool_model.monthly_cost),
                    active_users_count=tool_model.active_users_count,
                    cost_per_user=cost_per_user,
                    department=tool_model.owner_department.value,
                    vendor=tool_model.vendor,
                    efficiency_rating=efficiency_rating
                )
            )
        
        # Calculer potential_savings sur TOUS les outils (pas seulement ceux limités)
        potential_savings = 0.0
        for tool_model in all_tools:
            cost_per_user = (
                float(tool_model.monthly_cost) / tool_model.active_users_count
                if tool_model.active_users_count > 0 else 0.0
            )
            efficiency_rating = self._calculate_efficiency_rating(
                cost_per_user,
                avg_cost_per_user_company
            )
            if efficiency_rating == EfficiencyRating.LOW:
                potential_savings += float(tool_model.monthly_cost)
        
        # Construire l'analyse
        analysis = ExpensiveToolsAnalysis(
            total_tools_analyzed=len(all_tools),
            avg_cost_per_user_company=avg_cost_per_user_company,
            potential_savings_identified=potential_savings
        )
        
        return ExpensiveToolsResponse(
            data=expensive_tool_items,
            analysis=analysis
        )
    
    def _calculate_efficiency_rating(
        self, 
        cost_per_user: float, 
        avg_cost_per_user_company: float
    ) -> EfficiencyRating:
        """
        Calcule le rating d'efficacité basé sur la comparaison avec la moyenne.
        
        Args:
            cost_per_user: Coût par utilisateur de l'outil
            avg_cost_per_user_company: Coût moyen par utilisateur de l'entreprise
            
        Returns:
            EfficiencyRating: Rating d'efficacité
        """
        if avg_cost_per_user_company == 0:
            # Si pas de moyenne disponible, retourner "average"
            return EfficiencyRating.AVERAGE
        
        ratio = cost_per_user / avg_cost_per_user_company
        
        if ratio < 0.5:
            return EfficiencyRating.EXCELLENT
        elif ratio < 0.8:
            return EfficiencyRating.GOOD
        elif ratio <= 1.2:
            return EfficiencyRating.AVERAGE
        else:
            return EfficiencyRating.LOW