import math

from app.repositories import ToolRepository
from app.schemas import Tool, ToolFilters, ToolsListResponse, NoResultsFoundResponse, PaginationInfo, ToolDetailResponse, NotFoundResponse


class ToolService:
    """Service pour la logique métier des outils."""
    
    def __init__(self, tool_repository: ToolRepository):
        self._repository = tool_repository
    
    def get_tool(self, tool_id: int) -> ToolDetailResponse | NotFoundResponse:
        """Récupère un outil par son ID."""
        tool_model = self._repository.get_tool(tool_id)
        
        if not tool_model:
            return NotFoundResponse()
        
        # TODO: Implémenter la logique métier pour usage_metrics et total_monthly_cost
        # Pour l'instant, valeurs par défaut
        from app.schemas import UsageMetrics, SessionMetrics
        
        tool = Tool.model_validate(tool_model)
        usage_metrics = UsageMetrics(
            last_30_days=SessionMetrics(
                total_sessions=0,
                avg_session_minutes=0
            )
        )
        total_monthly_cost = 0
        
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

