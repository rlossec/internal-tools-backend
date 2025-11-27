from datetime import datetime, timedelta
import math

from fastapi import HTTPException, status

from app.repositories import ToolRepository
from app.schemas import Tool, ToolFilters, ToolsListResponse, NoResultsFoundResponse, PaginationInfo, ToolDetailResponse, NotFoundResponse, UsageMetrics, SessionMetrics, ToolCreateRequest, ToolCreateResponse, ToolUpdateRequest, ToolUpdateResponse
from app.models.enum_types import DepartmentType, ToolStatus


class ToolService:
    """Service pour la logique métier des outils."""
    
    def __init__(self, tool_repository: ToolRepository):
        self._repository = tool_repository
    
    def create_tool(self, tool_data: ToolCreateRequest) -> ToolCreateResponse:
        """Crée un nouvel outil."""
        
        department = DepartmentType(tool_data.owner_department)

        try:
            tool_model = self._repository.create_tool(
                name=tool_data.name,
                description=tool_data.description,
                vendor=tool_data.vendor,
                website_url=tool_data.website_url,
                category_id=tool_data.category_id,
                monthly_cost=tool_data.monthly_cost,
                owner_department=department,
            )
        except ValueError as e:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        
        # Convertir en ToolCreateResponse
        return ToolCreateResponse.model_validate(tool_model)
    
    def update_tool(self, tool_id: int, tool_data: ToolUpdateRequest) -> ToolUpdateResponse:
        """Met à jour un outil existant."""
        # Récupérer les champs explicitement fournis (exclure ceux non fournis)
        provided_fields = tool_data.model_dump(exclude_unset=True)
        
        # Convertir enums si fournis
        owner_department_enum = ...
        if "owner_department" in provided_fields:
            if provided_fields["owner_department"] is not None:
                owner_department_enum = DepartmentType(provided_fields["owner_department"])
            else:
                owner_department_enum = None  # Explicitement fourni comme None
        
        status_enum = ...
        if "status" in provided_fields:
            if provided_fields["status"] is not None:
                status_enum = ToolStatus(provided_fields["status"])
            else:
                status_enum = None  # Explicitement fourni comme None
        
        # Préparer les paramètres pour le repository
        name = provided_fields.get("name", ...) if "name" in provided_fields else ...
        description = provided_fields.get("description", ...) if "description" in provided_fields else ...
        vendor = provided_fields.get("vendor", ...) if "vendor" in provided_fields else ...
        website_url = provided_fields.get("website_url", ...) if "website_url" in provided_fields else ...
        category_id = provided_fields.get("category_id", ...) if "category_id" in provided_fields else ...
        monthly_cost = provided_fields.get("monthly_cost", ...) if "monthly_cost" in provided_fields else ...
        
        # Mettre à jour via le repository
        try:
            tool_model = self._repository.update_tool(
                tool_id=tool_id,
                name=name,
                description=description,
                vendor=vendor,
                website_url=website_url,
                category_id=category_id,
                monthly_cost=monthly_cost,
                owner_department=owner_department_enum,
                status=status_enum,
            )
        except ValueError as e:
            # Erreur de catégorie inexistante
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        
        if not tool_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool with id {tool_id} not found"
            )
        
        # Convertir en ToolUpdateResponse
        return ToolUpdateResponse.model_validate(tool_model)
    
    def get_tool(self, tool_id: int) -> ToolDetailResponse:
        """Récupère un outil par son ID."""
        tool_model = self._repository.get_tool(tool_id)
        
        if not tool_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool with id {tool_id} not found"
            )

        tool = Tool.model_validate(tool_model)
        
        # Calcul des métriques d'utilisation (30 derniers jours)
        usage_metrics = self.get_tool_usage_metrics_last_days(tool_id, days_number=30)
        
        # Calcul du coût total mensuel
        total_monthly_cost = self.get_tool_total_monthly_cost(tool_id)
        
        return ToolDetailResponse(
            **tool.model_dump(),
            total_monthly_cost=total_monthly_cost,
            usage_metrics=usage_metrics
        )
    
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

    def get_tool_total_monthly_cost(self, tool_id: int) -> float:
        """
        Calcule le coût total mensuel d'un outil.
        
        Formule : monthly_cost * active_users_count
        """
        tool = self._repository.get_tool(tool_id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found"
            )

        total_monthly_cost = float(tool.monthly_cost) * tool.active_users_count
        
        return total_monthly_cost
    
    def get_tool_usage_metrics_last_days(self, tool_id: int, days_number: int) -> UsageMetrics:
        """
        Récupère les métriques d'utilisation d'un outil pour les N derniers jours.
        """
        tool = self._repository.get_tool(tool_id)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool not found"
            )

        usage_logs = self._repository.get_tool_usage_logs(tool_id)
        # Filtrer les logs des N derniers jours
        # FAKE_DATE = date(2025, 6, 1) pour les tests
        cutoff_date = datetime.now().date() - timedelta(days=days_number)
        filtered_logs = [
            log for log in usage_logs 
            if log.session_date >= cutoff_date
        ]
        total_sessions = len(filtered_logs)
        total_minutes = sum(log.usage_minutes for log in filtered_logs)
        
        # Éviter la division par zéro
        avg_session_minutes = total_minutes / total_sessions if total_sessions > 0 else 0
        
        return UsageMetrics(
            last_30_days=SessionMetrics(
                total_sessions=total_sessions,
                avg_session_minutes=int(avg_session_minutes)
            )
        )