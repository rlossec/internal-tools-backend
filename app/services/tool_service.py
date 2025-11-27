import math

from app.repositories import ToolRepository
from app.schemas import Tool, ToolFilters, ToolsListResponse, NoResultsFoundResponse, PaginationInfo


class ToolService:
    """Service pour la logique métier des outils."""
    
    def __init__(self, tool_repository: ToolRepository):
        self._repository = tool_repository
    
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

