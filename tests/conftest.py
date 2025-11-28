"""Configuration et fixtures communes pour tous les tests."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base
from app.repositories import ToolRepository
from app.services import ToolService
from app.router.dependencies import get_tool_service
from app.main import app

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Crée une session de base de données de test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Charger automatiquement les fixtures de données
pytest_plugins = ["tests.fixtures.data"]


@pytest.fixture
def tool_repository(db_session):
    """Crée un repository de test."""
    return ToolRepository(session=db_session)


@pytest.fixture
def tool_service(tool_repository):
    """Crée un service de test."""
    return ToolService(tool_repository=tool_repository)


def create_override_get_tool_service(db_session):
    """Crée une fonction override de la dépendance pour les tests."""
    def override_get_tool_service():
        repository = ToolRepository(session=db_session)
        yield ToolService(tool_repository=repository)
    return override_get_tool_service


@pytest.fixture
def client(db_session, test_categories, test_tools):
    """Crée un client de test FastAPI."""
    # Override de la dépendance pour utiliser la session de test
    app.dependency_overrides[get_tool_service] = create_override_get_tool_service(db_session)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


