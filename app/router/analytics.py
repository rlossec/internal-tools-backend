from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.router.dependencies import get_department_service, get_tool_service
from app.services import DepartmentService, ToolService
from app.schemas import (
    DepartmentCostsResponse,
    SortDepartmentCostField,
    SortOrder,
    ExpensiveToolsResponse
)


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/department-costs",
    response_model=DepartmentCostsResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Coûts des départements"
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Erreur de validation"
        }
    },
    summary="Récupère les coûts des départements."
)
async def get_department_costs(
    department_service: DepartmentService = Depends(get_department_service),
    sort_by: Optional[SortDepartmentCostField] = Query(
        SortDepartmentCostField.TOTAL_COST,
        description="Champ de tri (department ou total_cost)"
    ),
    order: Optional[SortOrder] = Query(
        SortOrder.DESC,
        description="Ordre de tri (asc ou desc)"
    ),
):
    return department_service.get_department_costs(
        sort_by=sort_by or SortDepartmentCostField.TOTAL_COST,
        order=order or SortOrder.DESC
    )


@router.get(
    "/expensive-tools",
    response_model=ExpensiveToolsResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Top outils coûteux avec analyse d'efficacité"
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Erreur de validation"
        }
    },
    summary="Récupère les outils les plus coûteux avec analyse d'efficacité."
)
async def get_expensive_tools(
    tool_service: ToolService = Depends(get_tool_service),
    min_cost: Optional[float] = Query(
        None,
        description="Coût minimum pour filtrer les outils",
        ge=0
    ),
    limit: Optional[int] = Query(
        None,
        description="Nombre maximum d'outils à retourner",
        ge=1,
        le=100
    ),
):
    """
    Récupère les outils les plus coûteux avec analyse d'efficacité.
    """
    return tool_service.get_expensive_tools(min_cost=min_cost, limit=limit)
