"""
Gestionnaires d'exceptions.
"""
from typing import Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError

from app.core.errors import ResourceNotFoundError


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Gestionnaire personnalisé pour les erreurs de validation FastAPI.
    
    Retourne HTTP 400 avec le format standardisé.
    """
    details: Dict[str, str] = {}
    
    for error in exc.errors():
        field_path = error["loc"]
        field_parts = [str(loc) for loc in field_path if loc not in ("body", "query")]
        field = ".".join(field_parts) if field_parts else "body"
        
        # Utiliser directement le message d'erreur du validator
        error_msg = error.get("msg", "")
        error_type = error.get("type", "")
        
        # Pour les erreurs "missing", formater un message standard
        if error_type == "missing":
            field_name = field.replace("_", " ").title()
            error_msg = f"{field_name} is required"
        # Pour les erreurs de type FastAPI Query (value_error, type_error, etc.)
        elif "value_error" in error_type or "type_error" in error_type:
            # Simplifier les messages FastAPI verbeux pour les enums
            if "enum" in error_type or "literal" in error_type:
                if "Input should be" in error_msg:
                    # Extraire les valeurs possibles du message
                    error_msg = "Must be one of the allowed values"
        
        # Si plusieurs erreurs pour le même champ, les combiner
        if field in details:
            details[field] += f"; {error_msg}"
        else:
            details[field] = error_msg
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation failed",
            "details": details
        }
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Gestionnaire personnalisé pour les erreurs de validation Pydantic.
    
    Retourne HTTP 400 avec le format standardisé.
    """
    details: Dict[str, str] = {}
    
    for error in exc.errors():
        # Extraire le nom du champ
        field = ".".join(str(loc) for loc in error["loc"])
        
        if not field:
            field = "body"
        
        # Utiliser directement le message d'erreur du validator
        error_msg = error.get("msg", "")
        error_type = error.get("type", "")
        
        # Pour les erreurs "missing", formater un message standard
        if error_type == "missing":
            field_name = field.replace("_", " ").title()
            error_msg = f"{field_name} is required"
        
        # Si plusieurs erreurs pour le même champ, les combiner
        if field in details:
            details[field] += f"; {error_msg}"
        else:
            details[field] = error_msg
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation failed",
            "details": details
        }
    )


async def database_exception_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """
    Gestionnaire pour les erreurs de base de données.
    
    Retourne une erreur HTTP 500 avec un message d'erreur standardisé
    lorsque la base de données n'est pas accessible.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "Database connection failed"
        }
    )


async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """
    Gestionnaire pour les erreurs ResourceNotFoundError.
    
    Transforme les exceptions de domaine en réponse HTTP 404 formatée.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": exc.error_type,
            "message": str(exc)
        }
    )
