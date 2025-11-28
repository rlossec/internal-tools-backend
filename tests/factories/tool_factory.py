"""Factory pour créer des outils de test."""
from typing import Optional
from datetime import datetime

from app.models import Tool
from app.models.enum_types import DepartmentType, ToolStatus
from tests.factories.base import BaseFactory


class ToolFactory(BaseFactory):
    """Factory pour créer des outils de test."""
    
    DEFAULT_VALUES = {
        "name": "Test Tool",
        "description": "Outil de test",
        "vendor": "Test Vendor",
        "website_url": "https://example.com",
        "monthly_cost": 50.0,
        "active_users_count": 0,
        "owner_department": DepartmentType.Engineering,
        "status": ToolStatus.active,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    def create(
        self,
        category_id: int,  # Requis
        name: Optional[str] = None,
        description: Optional[str] = None,
        vendor: Optional[str] = None,
        website_url: Optional[str] = None,
        monthly_cost: Optional[float] = None,
        active_users_count: Optional[int] = None,
        owner_department: Optional[DepartmentType] = None,
        status: Optional[ToolStatus] = None,
        **kwargs
    ) -> Tool:
        """Crée un outil avec des valeurs par défaut."""
        values = self.DEFAULT_VALUES.copy()
        values.update({
            "category_id": category_id,
            "name": name or values["name"],
            "description": description or values["description"],
            "vendor": vendor or values["vendor"],
            "website_url": website_url or values["website_url"],
            "monthly_cost": monthly_cost if monthly_cost is not None else values["monthly_cost"],
            "active_users_count": active_users_count if active_users_count is not None else values["active_users_count"],
            "owner_department": owner_department or values["owner_department"],
            "status": status or values["status"],
            **kwargs
        })
        return self._create(Tool, **values)
    
    def create_github(self, category_id: int) -> Tool:
        """Crée un outil GitHub."""
        return self.create(
            category_id=category_id,
            name="GitHub",
            description="Plateforme de gestion de code",
            vendor="GitHub Inc.",
            website_url="https://github.com",
            monthly_cost=50.0,
            owner_department=DepartmentType.Engineering,
            status=ToolStatus.active
        )
    
    def create_slack(self, category_id: int) -> Tool:
        """Crée un outil Slack."""
        return self.create(
            category_id=category_id,
            name="Slack",
            description="Outil de communication",
            vendor="Slack Technologies",
            website_url="https://slack.com",
            monthly_cost=75.0,
            owner_department=DepartmentType.Marketing,
            status=ToolStatus.active
        )
    
    def create_jira(self, category_id: int) -> Tool:
        """Crée un outil Jira."""
        return self.create(
            category_id=category_id,
            name="Jira",
            description="Gestion de projet",
            vendor="Atlassian",
            website_url="https://jira.com",
            monthly_cost=100.0,
            owner_department=DepartmentType.Engineering,
            status=ToolStatus.trial
        )
    
    def create_figma(self, category_id: int) -> Tool:
        """Crée un outil Figma."""
        return self.create(
            category_id=category_id,
            name="Figma",
            description="Outil de design",
            vendor="Figma Inc.",
            website_url="https://figma.com",
            monthly_cost=30.0,
            owner_department=DepartmentType.Design,
            status=ToolStatus.active
        )
    
    def create_inactive(self, category_id: int, **kwargs) -> Tool:
        """Crée un outil inactif (déprécié)."""
        return self.create(
            category_id=category_id,
            status=ToolStatus.deprecated,
            **kwargs
        )
    
    def create_trial(self, category_id: int, **kwargs) -> Tool:
        """Crée un outil en trial."""
        return self.create(
            category_id=category_id,
            status=ToolStatus.trial,
            **kwargs
        )
    
    def create_with_cost(self, category_id: int, cost: float, **kwargs) -> Tool:
        """Crée un outil avec un coût spécifique."""
        return self.create(
            category_id=category_id,
            monthly_cost=cost,
            **kwargs
        )
    
    def create_for_department(
        self,
        category_id: int,
        department: DepartmentType,
        **kwargs
    ) -> Tool:
        """Crée un outil pour un département spécifique."""
        return self.create(
            category_id=category_id,
            owner_department=department,
            **kwargs
        )

