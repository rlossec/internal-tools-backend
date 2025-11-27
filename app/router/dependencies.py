from typing import Optional

from fastapi import Depends, Query

from app.db.database import SessionLocal
from app.repositories.tool_repository import ToolRepository
from app.services.tool_service import ToolService
from app.schemas import ToolFilters, SortToolField, SortOrder


def get_tool_repository():
    db = SessionLocal()
    try:
        yield ToolRepository(session=db)
    finally:
        db.close()


def get_tool_service(tool_repository: ToolRepository = Depends(get_tool_repository)):
    """Dépendance pour obtenir le ToolService."""
    yield ToolService(tool_repository=tool_repository)


def get_tool_filters(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    vendor: Optional[str] = Query(None, description="Filtrer par vendeur"),
    department: Optional[str] = Query(None, description="Filtrer par département"),
    tool_status: Optional[str] = Query(None, description="Filtrer par statut", alias="status"),
    max_cost: Optional[float] = Query(None, description="Coût maximum", ge=0),
    min_cost: Optional[float] = Query(None, description="Coût minimum", ge=0),
    sort_by: Optional[SortToolField] = Query(None, description="Champ de tri"),
    sort_order: Optional[SortOrder] = Query(None, description="Ordre de tri (asc/desc)"),
    page: Optional[int] = Query(None, description="Numéro de page (commence à 1)", ge=1),
    limit: Optional[int] = Query(None, description="Nombre d'éléments par page (max 100)", ge=1, le=100),
) -> ToolFilters:
    """
    Dépendance pour construire les filtres à partir des paramètres de requête.
    
    Les erreurs de validation Pydantic sont automatiquement gérées par
    le gestionnaire pydantic_validation_exception_handler dans app/core/exceptions.py
    qui retourne un HTTP 400 avec le format standardisé.
    """
    return ToolFilters(
        category=category,
        vendor=vendor,
        department=department,
        status=tool_status,
        max_cost=max_cost,
        min_cost=min_cost,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )


__all__ = ["get_tool_repository", "get_tool_service", "get_tool_filters"]