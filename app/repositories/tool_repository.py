from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Tool as ToolModel, Category, UsageLog
from app.models.enum_types import DepartmentType, ToolStatus
from app.schemas import ToolFilters, SortToolField, SortOrder
from app.core.errors import CategoryNotFoundError, ToolNotFoundError


class ToolRepository:

    def __init__(self, session: Session):
        self._db = session

    def _apply_filters(self, query, filters: ToolFilters):
        if not filters:
            return query

        if filters.category:
            query = query.filter(Category.name.ilike(f"%{filters.category}%"))

        if filters.vendor:
            query = query.filter(ToolModel.vendor.ilike(f"%{filters.vendor}%"))

        if filters.department:
            try:
                dept_enum = DepartmentType(filters.department)
                query = query.filter(ToolModel.owner_department == dept_enum)
            except ValueError:
                pass

        if filters.status:
            try:
                status_enum = ToolStatus(filters.status)
                query = query.filter(ToolModel.status == status_enum)
            except ValueError:
                pass

        if filters.min_cost is not None:
            query = query.filter(ToolModel.monthly_cost >= filters.min_cost)

        if filters.max_cost is not None:
            query = query.filter(ToolModel.monthly_cost <= filters.max_cost)

        return query

    def _get_sort_column(self, sort_field: SortToolField):
        mapping = {
            SortToolField.ID: ToolModel.id,
            SortToolField.NAME: ToolModel.name,
            SortToolField.MONTHLY_COST: ToolModel.monthly_cost,
            SortToolField.CREATED_AT: ToolModel.created_at,
        }
        return mapping.get(sort_field)

    def count_all(self) -> int:
        return self._db.query(ToolModel).count()

    def list_tools(self, filters: ToolFilters) -> List[ToolModel]:
        query = self._db.query(ToolModel).join(Category)
        query = self._apply_filters(query, filters)
        
        # Tri
        if filters.sort_by:
            sort_column = self._get_sort_column(filters.sort_by)
            if sort_column:
                if filters.sort_order == SortOrder.DESC:
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(ToolModel.id.asc())

        # Pagination
        if filters.page is not None and filters.limit is not None:
            offset = (filters.page - 1) * filters.limit
            query = query.offset(offset).limit(filters.limit)

        return query.all()

    def count_filtered(self, filters: ToolFilters) -> int:
        query = self._db.query(ToolModel).join(Category)
        query = self._apply_filters(query, filters)
        return query.count()

    def get_tool(self, tool_id: int) -> ToolModel:
        return self._db.query(ToolModel).filter(ToolModel.id == tool_id).first()

    def get_tool_usage_logs(self, tool_id: int) -> List[UsageLog]:
        """Récupère tous les logs d'utilisation pour un outil donné."""
        return self._db.query(UsageLog).filter(UsageLog.tool_id == tool_id).all()

    def create_tool(
        self,
        name: str,
        description: Optional[str],
        vendor: str,
        website_url: Optional[str],
        category_id: int,
        monthly_cost: float,
        owner_department: DepartmentType,
    ) -> ToolModel:
        """Crée un nouvel outil."""
        # Vérifier que la catégorie existe
        category = self._db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise CategoryNotFoundError(category_id)
        
        tool = ToolModel(
            name=name,
            description=description,
            vendor=vendor,
            website_url=website_url,
            category_id=category_id,
            monthly_cost=monthly_cost,
            active_users_count=0,
            owner_department=owner_department,
            status=ToolStatus.active,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._db.add(tool)
        self._db.commit()
        self._db.refresh(tool)
        
        return tool
    
    def update_tool(
        self,
        tool_id: int,
        name: Optional[str] = ...,
        description: Optional[str] = ...,
        vendor: Optional[str] = ...,
        website_url: Optional[str] = ...,
        category_id: Optional[int] = ...,
        monthly_cost: Optional[float] = ...,
        owner_department: Optional[DepartmentType] = ...,
        status: Optional[ToolStatus] = ...,
    ) -> Optional[ToolModel]:
        """Met à jour un outil existant."""
        tool = self._db.query(ToolModel).filter(ToolModel.id == tool_id).first()
        if not tool:
            raise ToolNotFoundError(tool_id)
        
        # Vérifier que la catégorie existe si category_id est fourni
        if category_id is not ...:
            category = self._db.query(Category).filter(Category.id == category_id).first()
            if not category:
                raise CategoryNotFoundError(category_id)
        
        # Mettre à jour uniquement les champs fournis (utiliser Ellipsis pour détecter les champs non fournis)
        if name is not ...:
            tool.name = name
        if description is not ...:
            tool.description = description
        if vendor is not ...:
            tool.vendor = vendor
        if website_url is not ...:
            tool.website_url = website_url
        if category_id is not ...:
            tool.category_id = category_id
        if monthly_cost is not ...:
            tool.monthly_cost = monthly_cost
        if owner_department is not ...:
            tool.owner_department = owner_department
        if status is not ...:
            tool.status = status
        
        # Mettre à jour updated_at
        tool.updated_at = datetime.now()
        
        self._db.commit()
        self._db.refresh(tool)
        
        return tool

    