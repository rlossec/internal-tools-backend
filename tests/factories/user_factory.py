"""Factory pour créer des utilisateurs de test."""
from typing import Optional
from datetime import datetime

from app.models import User
from app.models.enum_types import DepartmentType, UserRole, UserStatus
from tests.factories.base import BaseFactory


class UserFactory(BaseFactory):
    """Factory pour créer des utilisateurs de test."""
    
    DEFAULT_VALUES = {
        "name": "Test User",
        "email": "test@example.com",
        "department": DepartmentType.Engineering,
        "role": UserRole.employee,
        "status": UserStatus.active,
        "created_at": datetime.now()
    }
    
    def create(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        department: Optional[DepartmentType] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        **kwargs
    ) -> User:
        """Crée un utilisateur avec des valeurs par défaut."""
        values = self.DEFAULT_VALUES.copy()
        values.update({
            "name": name or values["name"],
            "email": email or values["email"],
            "department": department or values["department"],
            "role": role or values["role"],
            "status": status or values["status"],
            **kwargs
        })
        return self._create(User, **values)
    
    def create_engineer(self, name: Optional[str] = None, email: Optional[str] = None) -> User:
        """Crée un utilisateur Engineering."""
        return self.create(
            name=name or "Engineer",
            email=email or f"{name or 'engineer'}@example.com",
            department=DepartmentType.Engineering
        )
    
    def create_sales(self, name: Optional[str] = None, email: Optional[str] = None) -> User:
        """Crée un utilisateur Sales."""
        return self.create(
            name=name or "Sales User",
            email=email or f"{name or 'sales'}@example.com",
            department=DepartmentType.Sales
        )
    
    def create_marketing(self, name: Optional[str] = None, email: Optional[str] = None) -> User:
        """Crée un utilisateur Marketing."""
        return self.create(
            name=name or "Marketing User",
            email=email or f"{name or 'marketing'}@example.com",
            department=DepartmentType.Marketing
        )
    
    def create_hr(self, name: Optional[str] = None, email: Optional[str] = None) -> User:
        """Crée un utilisateur HR."""
        return self.create(
            name=name or "HR User",
            email=email or f"{name or 'hr'}@example.com",
            department=DepartmentType.HR
        )
    
    def create_admin(self, department: Optional[DepartmentType] = None) -> User:
        """Crée un utilisateur admin."""
        return self.create(
            name="Admin User",
            email="admin@example.com",
            role=UserRole.admin,
            department=department or DepartmentType.Engineering
        )
    
    def create_manager(self, department: Optional[DepartmentType] = None) -> User:
        """Crée un utilisateur manager."""
        return self.create(
            name="Manager User",
            email="manager@example.com",
            role=UserRole.manager,
            department=department or DepartmentType.Engineering
        )
    
    def create_inactive(self, **kwargs) -> User:
        """Crée un utilisateur inactif."""
        return self.create(
            status=UserStatus.inactive,
            **kwargs
        )
    
    def create_multiple_for_department(
        self,
        department: DepartmentType,
        count: int,
        prefix: str = "User"
    ) -> list[User]:
        """Crée plusieurs utilisateurs pour un département."""
        users = []
        for i in range(count):
            users.append(self.create(
                name=f"{prefix} {i+1}",
                email=f"{prefix.lower().replace(' ', '')}{i+1}@example.com",
                department=department
            ))
        return users

