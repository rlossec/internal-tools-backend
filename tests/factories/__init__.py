"""Factories pour créer des données de test facilement."""
import pytest

from tests.factories.base import BaseFactory
from tests.factories.category_factory import CategoryFactory
from tests.factories.tool_factory import ToolFactory
from tests.factories.user_factory import UserFactory
from tests.factories.user_tool_access_factory import UserToolAccessFactory
from tests.factories.usage_log_factory import UsageLogFactory
from tests.factories.cost_tracking_factory import CostTrackingFactory


class FactoryManager:
    """Manager centralisé pour toutes les factories."""
    
    def __init__(self, db_session):
        self.db = db_session
        self.category = CategoryFactory(db_session)
        self.tool = ToolFactory(db_session)
        self.user = UserFactory(db_session)
        self.user_tool_access = UserToolAccessFactory(db_session)
        self.usage_log = UsageLogFactory(db_session)
        self.cost_tracking = CostTrackingFactory(db_session)
    
    def commit(self):
        """Commit toutes les modifications."""
        self.db.commit()
    
    def rollback(self):
        """Annule toutes les modifications."""
        self.db.rollback()
    
    def flush(self):
        """Flush toutes les modifications sans commit."""
        self.db.flush()


@pytest.fixture
def factories(db_session):
    return FactoryManager(db_session)


__all__ = [
    "BaseFactory",
    "CategoryFactory",
    "ToolFactory",
    "UserFactory",
    "UserToolAccessFactory",
    "UsageLogFactory",
    "CostTrackingFactory",
    "FactoryManager",
    "factories",
]

