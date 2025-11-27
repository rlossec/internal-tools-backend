from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.tool import Tool as ToolModel
from app.models.category import Category
from app.models.enum_types import DepartmentType, ToolStatus
from app.schemas.tool import ToolFilters, SortToolField
from app.schemas.common import SortOrder


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

    
