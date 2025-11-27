from datetime import datetime, timedelta
import math

from fastapi import HTTPException, status

from app.repositories import ToolRepository
from app.schemas import Tool, ToolFilters, ToolsListResponse, NoResultsFoundResponse, PaginationInfo, ToolDetailResponse, NotFoundResponse, UsageMetrics, SessionMetrics

class ToolService:
    """Service pour la logique métier des outils."""
    
    def __init__(self, tool_repository: ToolRepository):
        self._repository = tool_repository
    
    def get_tool(self, tool_id: int) -> ToolDetailResponse | NotFoundResponse:
        """Récupère un outil par son ID."""
        tool_model = self._repository.get_tool(tool_id)
        
        if not tool_model:
            return NotFoundResponse()
        
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found"
            )

        total_monthly_cost = float(tool.monthly_cost) * tool.active_users_count
        
        return total_monthly_cost
    
    def get_tool_usage_metrics_last_days(self, tool_id: int, days_number: int) -> UsageMetrics:
        """
        Récupère les métriques d'utilisation d'un outil pour les N derniers jours.
        """
        tool = self._repository.get_tool(tool_id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found"
            )

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