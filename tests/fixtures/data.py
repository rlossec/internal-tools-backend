"""Fixtures pour les données de test (catégories, outils, utilisateurs, logs)."""
import pytest
from datetime import datetime, date, timedelta

from app.models import Category, Tool, User, UsageLog
from app.models.enum_types import DepartmentType, ToolStatus, UserRole, UserStatus


@pytest.fixture(scope="function")
def test_categories(db_session):
    """Crée des catégories de test."""
    categories = [
        Category(
            id=1,
            name="Development",
            description="Outils de développement",
            color_hex="#10b981",
            created_at=datetime.now()
        ),
        Category(
            id=2,
            name="Design",
            description="Outils de design",
            color_hex="#f59e0b",
            created_at=datetime.now()
        ),
        Category(
            id=3,
            name="Marketing",
            description="Outils de marketing",
            color_hex="#ef4444",
            created_at=datetime.now()
        ),
        Category(
            id=4,
            name="Operations",
            description="Outils d'opérations",
            color_hex="#ec4899",
            created_at=datetime.now()
        ),
        Category(
            id=5,
            name="Finance",
            description="Outils de finance",
            color_hex="#6366f1",
            created_at=datetime.now()
        )
    ]
    
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


@pytest.fixture(scope="function")
def test_user(db_session):
    """Crée un utilisateur de test pour les logs d'utilisation."""
    user = User(
        id=1,
        name="Test User",
        email="test@example.com",
        department=DepartmentType.Engineering,
        role=UserRole.employee,
        status=UserStatus.active,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_usage_logs(db_session, test_tools, test_user):
    """Crée des logs d'utilisation de test pour tester les métriques."""
    today = date.today()
    
    usage_logs = [
        # Logs récents (dans les 30 derniers jours)
        UsageLog(
            id=1,
            user_id=test_user.id,
            tool_id=test_tools[0].id,  # GitHub
            session_date=today - timedelta(days=5),
            usage_minutes=120,
            actions_count=50,
            created_at=datetime.now()
        ),
        UsageLog(
            id=2,
            user_id=test_user.id,
            tool_id=test_tools[0].id,  # GitHub
            session_date=today - timedelta(days=10),
            usage_minutes=90,
            actions_count=30,
            created_at=datetime.now()
        ),
        UsageLog(
            id=3,
            user_id=test_user.id,
            tool_id=test_tools[0].id,  # GitHub
            session_date=today - timedelta(days=15),
            usage_minutes=60,
            actions_count=20,
            created_at=datetime.now()
        ),
        # Logs anciens (hors des 30 derniers jours)
        UsageLog(
            id=4,
            user_id=test_user.id,
            tool_id=test_tools[0].id,  # GitHub
            session_date=today - timedelta(days=35),
            usage_minutes=200,
            actions_count=100,
            created_at=datetime.now()
        ),
        # Logs pour un autre outil (Slack)
        UsageLog(
            id=5,
            user_id=test_user.id,
            tool_id=test_tools[1].id,  # Slack
            session_date=today - timedelta(days=7),
            usage_minutes=180,
            actions_count=60,
            created_at=datetime.now()
        ),
    ]
    
    for log in usage_logs:
        db_session.add(log)
    db_session.commit()
    
    for log in usage_logs:
        db_session.refresh(log)
    
    return usage_logs

