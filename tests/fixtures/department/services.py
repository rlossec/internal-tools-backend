"""Fixtures pour les services et repositories pour les départements."""
import pytest


@pytest.fixture
def department_repository(db_session):
    """Crée un repository de département de test."""
    from app.repositories import DepartmentRepository
    return DepartmentRepository(session=db_session)


@pytest.fixture
def department_service(department_repository):
    """Crée un service pour les départements de test."""
    from app.services.department.department_service import DepartmentService
    return DepartmentService(department_repository=department_repository)

