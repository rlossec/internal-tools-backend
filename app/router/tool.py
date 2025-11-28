from typing import Union

from fastapi import APIRouter, Depends, status

from app.router.dependencies import get_tool_service, get_tool_filters
from app.services import ToolService

from app.schemas import NoResultsFoundResponse, ToolsListResponse, ToolDetailResponse, ToolFilters, ToolCreateRequest, ToolCreateResponse, ToolUpdateRequest, ToolUpdateResponse


router = APIRouter(prefix="/tools", tags=["tools"])

@router.get(
    "",
    response_model=Union[ToolsListResponse, NoResultsFoundResponse],
    responses={
        status.HTTP_200_OK: {
            "description": "Liste des outils"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Aucun outil trouvé"
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Erreur de validation"
        }
    },
    summary="Récupère la liste des outils avec filtres, tri et pagination."
)
async def get_tools(
    tool_service: ToolService = Depends(get_tool_service),
    filters: ToolFilters = Depends(get_tool_filters),
):
    """Récupère la liste des outils avec filtres et tri."""
    return tool_service.list_tools(filters)


@router.post(
    "",
    response_model=ToolCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Outil créé avec succès"
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Erreur de validation"
        }
    },
    summary="Crée un nouvel outil."
)
async def create_tool(
    tool_data: ToolCreateRequest,
    tool_service: ToolService = Depends(get_tool_service),
):
    """Crée un nouvel outil."""
    return tool_service.create_tool(tool_data)


@router.get(
    "/{tool_id}",
    response_model=ToolDetailResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Outil trouvé"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Outil non trouvé"
        }
    },
    summary="Récupère les détails d'un outil par son ID."
)
async def get_tool(
  tool_id: int,
    tool_service: ToolService = Depends(get_tool_service),
):
    """Récupère les détails d'un outil par son ID."""
    return tool_service.get_tool(tool_id)


@router.put(
    "/{tool_id}",
    response_model=ToolUpdateResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Outil mis à jour avec succès"
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Erreur de validation"
        }
    },
    summary="Met à jour un outil existant."
)
async def update_tool(
    tool_id: int,
    tool_data: ToolUpdateRequest,
    tool_service: ToolService = Depends(get_tool_service),
):
    """Met à jour un outil existant."""
    return tool_service.update_tool(tool_id, tool_data)
