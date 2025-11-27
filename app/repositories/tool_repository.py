
from typing import List

from sqlalchemy.orm import Session

from app.models.tool import Tool as ToolModel


class ToolRepository:

    def __init__(self, session: Session):
        self._db = session

    def list_tools(self) -> List[ToolModel]:
        """Récupère tous les outils avec leurs relations via l'ORM."""
        query = self._db.query(ToolModel)
        return query.all()

    def get_tool(self, tool_id: int) -> ToolModel:
        return self._db.query(ToolModel).filter(ToolModel.id == tool_id).first()
