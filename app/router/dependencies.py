
from app.db.database import SessionLocal
from app.repositories.tool_repository import ToolRepository


def get_tool_repository():
    db = SessionLocal()
    try:
        yield ToolRepository(session=db)
    finally:
        db.close()

__all__ = ["get_tool_repository"]