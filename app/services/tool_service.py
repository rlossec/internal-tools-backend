from app.repositories import ToolRepository
from app.schemas import Tool, ToolFilters, ToolsListResponse, NoResultsFoundResponse


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
        
        return ToolsListResponse(
            data=tools,
            total=total,
            filtered=filtered_total,
            filters_applied=filters.get_applied_filters()
        )

