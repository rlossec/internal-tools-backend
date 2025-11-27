from fastapi import APIRouter, Depends

from app.router.dependencies import get_tool_repository
from app.repositories import ToolRepository
from app.schemas.tool import Tool, ToolsListResponse

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("")
async def get_tools(
  tool_repository: ToolRepository = Depends(get_tool_repository)
):
    tool_models = tool_repository.list_tools()

    tools = [Tool.model_validate(tool_model) for tool_model in tool_models]
    
    response = ToolsListResponse(
        data=tools,
        total=len(tools),
        filtered=len(tools),
        filters_applied={}
    )
    
    return response