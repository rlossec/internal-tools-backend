"""Factory pour créer des accès utilisateur-outil."""
from typing import Optional
from datetime import datetime, timezone

from app.models import UserToolAccess
from app.models.enum_types import AccessStatus
from tests.factories.base import BaseFactory


class UserToolAccessFactory(BaseFactory):
    """Factory pour créer des accès utilisateur-outil."""
    
    DEFAULT_VALUES = {
        "status": AccessStatus.active,
        "granted_at": datetime.now(timezone.utc)
    }
    
    def create(
        self,
        user_id: int,
        tool_id: int,
        granted_by: int,
        status: Optional[AccessStatus] = None,
        revoked_at: Optional[datetime] = None,
        revoked_by: Optional[int] = None,
        **kwargs
    ) -> UserToolAccess:
        """Crée un accès utilisateur-outil."""
        values = self.DEFAULT_VALUES.copy()
        values.update({
            "user_id": user_id,
            "tool_id": tool_id,
            "granted_by": granted_by,
            "status": status or values["status"],
            "revoked_at": revoked_at,
            "revoked_by": revoked_by,
            **kwargs
        })
        return self._create(UserToolAccess, **values)
    
    def create_active(self, user_id: int, tool_id: int, granted_by: int) -> UserToolAccess:
        """Crée un accès actif."""
        return self.create(
            user_id=user_id,
            tool_id=tool_id,
            granted_by=granted_by,
            status=AccessStatus.active
        )
    
    def create_revoked(
        self,
        user_id: int,
        tool_id: int,
        granted_by: int,
        revoked_by: int
    ) -> UserToolAccess:
        """Crée un accès révoqué."""
        return self.create(
            user_id=user_id,
            tool_id=tool_id,
            granted_by=granted_by,
            status=AccessStatus.revoked,
            revoked_at=datetime.now(timezone.utc),
            revoked_by=revoked_by
        )
    
    def grant_access_to_multiple_tools(
        self,
        user_id: int,
        tool_ids: list[int],
        granted_by: int
    ) -> list[UserToolAccess]:
        """Donne accès à un utilisateur pour plusieurs outils."""
        accesses = []
        for tool_id in tool_ids:
            accesses.append(self.create_active(user_id, tool_id, granted_by))
        return accesses
    
    def grant_access_to_multiple_users(
        self,
        user_ids: list[int],
        tool_id: int,
        granted_by: int
    ) -> list[UserToolAccess]:
        """Donne accès à plusieurs utilisateurs pour un outil."""
        accesses = []
        for user_id in user_ids:
            accesses.append(self.create_active(user_id, tool_id, granted_by))
        return accesses

