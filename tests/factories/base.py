"""Factory de base pour créer des entités de test."""
from typing import Dict, Any, List
from sqlalchemy.orm import Session


class BaseFactory:
    """Factory de base pour créer des entités de test."""
    
    def __init__(self, db_session: Session):
        self._db = db_session
    
    def _create(self, model_class, **kwargs):
        """Méthode générique pour créer une entité."""
        instance = model_class(**kwargs)
        self._db.add(instance)
        self._db.flush()
        self._db.refresh(instance)
        return instance
    
    def _bulk_create(self, model_class, items: List[Dict[str, Any]]):
        """Créer plusieurs entités en une fois."""
        instances = []
        for item in items:
            instance = model_class(**item)
            self._db.add(instance)
            instances.append(instance)
        self._db.flush()
        for instance in instances:
            self._db.refresh(instance)
        return instances

