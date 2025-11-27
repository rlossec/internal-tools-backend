from typing import Union

from fastapi import APIRouter, Depends

from app.router.dependencies import get_tool_repository, get_tool_service, get_tool_filters
from app.repositories import ToolRepository
from app.services import ToolService

from app.schemas import NoResultsFoundResponse, NotFoundResponse, SessionMetrics, Tool, ToolsListResponse, ToolDetailResponse, UsageMetrics, ToolFilters


router = APIRouter(prefix="/tools", tags=["tools"])

@router.get(
    "",
    response_model=Union[ToolsListResponse, NoResultsFoundResponse]
)
async def get_tools(
    tool_service: ToolService = Depends(get_tool_service),
    filters: ToolFilters = Depends(get_tool_filters),
):
    """Récupère la liste des outils avec filtres et tri."""
    return tool_service.list_tools(filters)


@router.get(
    "/{tool_id}",
    response_model=Union[ToolDetailResponse, NotFoundResponse]
)
async def get_tool(
  tool_id: int,
  tool_repository: ToolRepository = Depends(get_tool_repository)
):
    tool_model = tool_repository.get_tool(tool_id)

    if not tool_model:
        return NotFoundResponse()
    
    tool = Tool.model_validate(tool_model)

    usage_metrics = UsageMetrics(
        last_30_days=SessionMetrics(
            total_sessions=0,
            avg_session_minutes=0
        )
    )
    
    total_monthly_cost = 0

    response = ToolDetailResponse(
        **tool.model_dump(),
        total_monthly_cost=total_monthly_cost,
        usage_metrics=usage_metrics
    )
    return response
