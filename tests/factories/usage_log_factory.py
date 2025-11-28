"""Factory pour créer des logs d'utilisation."""
from typing import Optional
from datetime import datetime, date, timedelta

from app.models import UsageLog
from tests.factories.base import BaseFactory


class UsageLogFactory(BaseFactory):
    """Factory pour créer des logs d'utilisation de test."""
    
    DEFAULT_VALUES = {
        "session_date": date.today(),
        "usage_minutes": 60,
        "actions_count": 10,
        "created_at": datetime.now()
    }
    
    def create(
        self,
        user_id: int,
        tool_id: int,
        session_date: Optional[date] = None,
        usage_minutes: Optional[int] = None,
        actions_count: Optional[int] = None,
        **kwargs
    ) -> UsageLog:
        """Crée un log d'utilisation avec des valeurs par défaut."""
        values = self.DEFAULT_VALUES.copy()
        values.update({
            "user_id": user_id,
            "tool_id": tool_id,
            "session_date": session_date or values["session_date"],
            "usage_minutes": usage_minutes if usage_minutes is not None else values["usage_minutes"],
            "actions_count": actions_count if actions_count is not None else values["actions_count"],
            **kwargs
        })
        return self._create(UsageLog, **values)
    
    def create_recent(
        self,
        user_id: int,
        tool_id: int,
        days_ago: int = 5,
        **kwargs
    ) -> UsageLog:
        """Crée un log récent (dans les 30 derniers jours)."""
        session_date = date.today() - timedelta(days=days_ago)
        return self.create(
            user_id=user_id,
            tool_id=tool_id,
            session_date=session_date,
            **kwargs
        )
    
    def create_old(
        self,
        user_id: int,
        tool_id: int,
        days_ago: int = 40,
        **kwargs
    ) -> UsageLog:
        """Crée un log ancien (hors des 30 derniers jours)."""
        session_date = date.today() - timedelta(days=days_ago)
        return self.create(
            user_id=user_id,
            tool_id=tool_id,
            session_date=session_date,
            **kwargs
        )
    
    def create_multiple_for_user(
        self,
        user_id: int,
        tool_id: int,
        count: int,
        start_days_ago: int = 0
    ) -> list[UsageLog]:
        """Crée plusieurs logs pour un utilisateur et un outil."""
        logs = []
        for i in range(count):
            session_date = date.today() - timedelta(days=start_days_ago + i)
            logs.append(self.create(
                user_id=user_id,
                tool_id=tool_id,
                session_date=session_date
            ))
        return logs

