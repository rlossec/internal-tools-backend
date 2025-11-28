"""Fixtures de données pour les tests de départements."""
import pytest
from datetime import date

from app.models.enum_types import DepartmentType


@pytest.fixture(scope="function")
def test_users_for_department_computations(factories):
    """Crée plusieurs utilisateurs dans différents départements."""
    # Créer l'admin
    admin_user = factories.user.create_admin()
    
    # Créer les utilisateurs Engineering
    engineer1 = factories.user.create_engineer(name="Engineer 1", email="engineer1@example.com")
    engineer2 = factories.user.create_engineer(name="Engineer 2", email="engineer2@example.com")
    engineer_inactive = factories.user.create_inactive(
        name="Engineer Inactive",
        email="engineer.inactive@example.com",
        department=DepartmentType.Engineering
    )
    
    # Créer les utilisateurs Sales
    sales1 = factories.user.create_sales(name="Sales 1", email="sales1@example.com")
    sales2 = factories.user.create_sales(name="Sales 2", email="sales2@example.com")
    
    # Créer l'utilisateur Marketing
    marketing1 = factories.user.create_marketing(name="Marketing 1", email="marketing1@example.com")
    
    # Créer l'utilisateur HR (sans outils)
    hr1 = factories.user.create_hr(name="HR 1", email="hr1@example.com")
    
    # Commit toutes les créations
    factories.commit()
    
    users = [
        admin_user,
        engineer1,
        engineer2,
        engineer_inactive,
        sales1,
        sales2,
        marketing1,
        hr1
    ]
    
    return {"users": users, "admin": admin_user}


@pytest.fixture(scope="function")
def test_user_tool_access_for_department_computations(factories, test_tools, test_users_for_department_computations):
    """Crée des accès utilisateur-outil pour les tests de calculs de département."""
    users = test_users_for_department_computations["users"]
    admin = test_users_for_department_computations["admin"]
    
    # Extraire les utilisateurs individuels
    # admin = users[0], engineer1 = users[1], engineer2 = users[2], etc.
    engineer1 = users[1]  # Engineer 1
    engineer2 = users[2]  # Engineer 2
    engineer_inactive = users[3]  # Engineer Inactive
    sales1 = users[4]  # Sales 1
    sales2 = users[5]  # Sales 2
    marketing1 = users[6]  # Marketing 1
    
    # Engineering - GitHub (tool 0)
    factories.user_tool_access.create_active(
        user_id=engineer1.id,
        tool_id=test_tools[0].id,  # GitHub
        granted_by=admin.id
    )
    factories.user_tool_access.create_active(
        user_id=engineer2.id,
        tool_id=test_tools[0].id,  # GitHub
        granted_by=admin.id
    )
    
    # Engineering - Jira (tool 2)
    factories.user_tool_access.create_active(
        user_id=engineer1.id,
        tool_id=test_tools[2].id,  # Jira
        granted_by=admin.id
    )
    
    # Sales - Slack (tool 1)
    factories.user_tool_access.create_active(
        user_id=sales1.id,
        tool_id=test_tools[1].id,  # Slack
        granted_by=admin.id
    )
    factories.user_tool_access.create_active(
        user_id=sales2.id,
        tool_id=test_tools[1].id,  # Slack
        granted_by=admin.id
    )
    
    # Marketing - Slack (tool 1)
    factories.user_tool_access.create_active(
        user_id=marketing1.id,
        tool_id=test_tools[1].id,  # Slack
        granted_by=admin.id
    )
    
    # Marketing - Figma (tool 3)
    factories.user_tool_access.create_active(
        user_id=marketing1.id,
        tool_id=test_tools[3].id,  # Figma
        granted_by=admin.id
    )
    
    # Accès révoqué (ne doit pas être compté)
    factories.user_tool_access.create_revoked(
        user_id=engineer1.id,
        tool_id=test_tools[3].id,  # Figma
        granted_by=admin.id,
        revoked_by=admin.id
    )
    
    # Utilisateur inactif avec accès (ne doit pas être compté)
    factories.user_tool_access.create_active(
        user_id=engineer_inactive.id,
        tool_id=test_tools[0].id,  # GitHub
        granted_by=admin.id
    )
    
    # Commit toutes les créations
    factories.commit()
    
    # Retourner tous les accès créés (optionnel, pour référence)
    # On pourrait aussi retourner une liste vide, car les accès sont déjà dans la DB
    return []


@pytest.fixture(scope="function")
def test_cost_tracking_for_department_computations(factories, test_tools):
    """Crée des CostTracking pour les tests de calculs de département."""
    current_month = date.today().replace(day=1)
    
    # GitHub (tool 0, id=1) - Engineering - 2 utilisateurs actifs, coût 50€/utilisateur = 100€ total
    factories.cost_tracking.create(
        tool_id=test_tools[0].id,  # GitHub (id=1)
        month_year=current_month,
        total_monthly_cost=100.00,  # 2 utilisateurs × 50€
        active_users_count=2
    )
    
    # Slack (tool 1, id=2) - Marketing (owner_department) - 3 utilisateurs actifs, coût 75€/utilisateur = 225€ total
    # Note: Dans la nouvelle logique, on utilise owner_department, donc Slack appartient à Marketing
    factories.cost_tracking.create(
        tool_id=test_tools[1].id,  # Slack (id=2)
        month_year=current_month,
        total_monthly_cost=225.00,  # 3 utilisateurs × 75€ (2 Sales + 1 Marketing)
        active_users_count=3
    )
    
    # Jira (tool 2, id=3) - Engineering - 1 utilisateur actif, coût 100€/utilisateur = 100€ total
    factories.cost_tracking.create(
        tool_id=test_tools[2].id,  # Jira (id=3)
        month_year=current_month,
        total_monthly_cost=100.00,  # 1 utilisateur × 100€
        active_users_count=1
    )
    
    # Figma (tool 3, id=4) - Design (owner_department) - 1 utilisateur actif, coût 30€/utilisateur = 30€ total
    factories.cost_tracking.create(
        tool_id=test_tools[3].id,  # Figma (id=4)
        month_year=current_month,
        total_monthly_cost=30.00,  # 1 utilisateur × 30€
        active_users_count=1
    )
    
    # Commit toutes les créations
    factories.commit()
    
    return []

