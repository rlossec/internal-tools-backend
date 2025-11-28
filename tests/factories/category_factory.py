"""Factory pour créer des catégories de test."""
from typing import Optional
from datetime import datetime

from app.models import Category
from tests.factories.base import BaseFactory


class CategoryFactory(BaseFactory):
    """Factory pour créer des catégories de test."""
    
    DEFAULT_VALUES = {
        "name": "Test Category",
        "description": "Description de test",
        "color_hex": "#6366f1",
        "created_at": datetime.now()
    }
    
    def create(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color_hex: Optional[str] = None,
        **kwargs
    ) -> Category:
        """Crée une catégorie avec des valeurs par défaut."""
        values = self.DEFAULT_VALUES.copy()
        values.update({
            "name": name or values["name"],
            "description": description or values["description"],
            "color_hex": color_hex or values["color_hex"],
            **kwargs
        })
        return self._create(Category, **values)
    
    def create_development(self) -> Category:
        """Crée une catégorie Development."""
        return self.create(
            name="Development",
            description="Outils de développement",
            color_hex="#10b981"
        )
    
    def create_design(self) -> Category:
        """Crée une catégorie Design."""
        return self.create(
            name="Design",
            description="Outils de design",
            color_hex="#f59e0b"
        )
    
    def create_marketing(self) -> Category:
        """Crée une catégorie Marketing."""
        return self.create(
            name="Marketing",
            description="Outils de marketing",
            color_hex="#ef4444"
        )
    
    def create_operations(self) -> Category:
        """Crée une catégorie Operations."""
        return self.create(
            name="Operations",
            description="Outils d'opérations",
            color_hex="#ec4899"
        )
    
    def create_finance(self) -> Category:
        """Crée une catégorie Finance."""
        return self.create(
            name="Finance",
            description="Outils de finance",
            color_hex="#6366f1"
        )
    
    def create_multiple(self, count: int, **overrides) -> list[Category]:
        """Crée plusieurs catégories."""
        categories = []
        for i in range(count):
            values = {"name": f"Category {i+1}", **overrides}
            categories.append(self.create(**values))
        return categories

