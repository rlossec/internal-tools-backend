"""Configuration et fixtures pour les tests."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base
from app.models.tool import Tool
from app.models.category import Category
from app.models.enum_types import DepartmentType, ToolStatus

from app.repositories.tool_repository import ToolRepository
from app.services.tool_service import ToolService
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


@pytest.fixture(scope="function")
def test_categories(db_session):
    """Crée une catégorie de test."""
    categories = [Category(
        id=1,
        name="Development",
        description="Outils de développement",
        color_hex="#10b981",
        created_at=datetime.now()
    ), Category(
        id=2,
        name="Design",
        description="Outils de design",
        color_hex="#f59e0b",
        created_at=datetime.now()
    ), Category(
        id=3,
        name="Marketing",
        description="Outils de marketing",
        color_hex="#ef4444",
        created_at=datetime.now()
    ), Category(
        id=4,
        name="Operations",
        description="Outils d'opérations",
        color_hex="#ec4899",
        created_at=datetime.now()
    ), Category(
        id=5,
        name="Finance",
        description="Outils de finance",
        color_hex="#6366f1",
        created_at=datetime.now()
    )]
    for category in categories:
        db_session.add(category)
    db_session.commit()
    for category in categories:
        db_session.refresh(category)
    return categories


@pytest.fixture(scope="function")
def test_tools(db_session, test_categories):
    """Crée plusieurs outils de test."""
    tools = [
        Tool(
            id=1,
            name="GitHub",
            description="Plateforme de gestion de code",
            vendor="GitHub Inc.",
            website_url="https://github.com",
            category_id=test_categories[0].id,
            monthly_cost=50.00,
            active_users_count=10,
            owner_department=DepartmentType.Engineering,
            status=ToolStatus.active,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1)
        ),
        Tool(
            id=2,
            name="Slack",
            description="Outil de communication",
            vendor="Slack Technologies",
            website_url="https://slack.com",
            category_id=test_categories[1].id,
            monthly_cost=75.00,
            active_users_count=25,
            owner_department=DepartmentType.Marketing,
            status=ToolStatus.active,
            created_at=datetime(2024, 2, 1),
            updated_at=datetime(2024, 2, 1)
        ),
        Tool(
            id=3,
            name="Jira",
            description="Gestion de projet",
            vendor="Atlassian",
            website_url="https://jira.com",
            category_id=test_categories[2].id,
            monthly_cost=100.00,
            active_users_count=15,
            owner_department=DepartmentType.Engineering,
            status=ToolStatus.trial,
            created_at=datetime(2024, 3, 1),
            updated_at=datetime(2024, 3, 1)
        ),
        Tool(
            id=4,
            name="Figma",
            description="Outil de design",
            vendor="Figma Inc.",
            website_url="https://figma.com",
            category_id=test_categories[3].id,
            monthly_cost=30.00,
            active_users_count=8,
            owner_department=DepartmentType.Design,
            status=ToolStatus.active,
            created_at=datetime(2024, 4, 1),
            updated_at=datetime(2024, 4, 1)
        ),
        Tool(
            id=5,
            name="Deprecated Tool",
            description="Outil obsolète",
            vendor="Old Vendor",
            website_url="https://old.com",
            category_id=test_categories[4].id,
            monthly_cost=20.00,
            active_users_count=0,
            owner_department=DepartmentType.Operations,
            status=ToolStatus.deprecated,
            created_at=datetime(2023, 1, 1),
            updated_at=datetime(2023, 1, 1)
        ),
    ]
    
    for tool in tools:
        db_session.add(tool)
    db_session.commit()
    
    for tool in tools:
        db_session.refresh(tool)
    
    return tools


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

