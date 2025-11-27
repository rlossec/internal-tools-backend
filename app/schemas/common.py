from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class NoResultsFoundResponse(BaseModel):
    message: str = "No results found"


class NotFoundResponse(BaseModel):
    message: str = "No resource with the given id found"


class ValidationErrorDetail(BaseModel):
    """Détail d'une erreur de validation."""
    field: str
    message: str
    type: str
    input: Optional[Any] = None


class ValidationErrorResponse(BaseModel):
    """Réponse standardisée pour les erreurs de validation."""
    detail: str
    errors: List[ValidationErrorDetail]