from typing import Union

from fastapi import APIRouter, Depends

from app.router.dependencies import get_tool_service, get_tool_filters
from app.services import ToolService

from app.schemas import NoResultsFoundResponse, NotFoundResponse, ToolsListResponse, ToolDetailResponse, ToolFilters


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
    tool_service: ToolService = Depends(get_tool_service),
):
    """Récupère les détails d'un outil par son ID."""
    return tool_service.get_tool(tool_id)
