from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.router.dependencies import get_department_service
from app.services import DepartmentService
from app.schemas import (
    DepartmentCostsResponse,
    SortDepartmentCostField,
    SortOrder
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
