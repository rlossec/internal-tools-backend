from fastapi import APIRouter, Depends

from app.router.dependencies import get_tool_repository
from app.repositories import ToolRepository
from app.schemas.tool import SessionMetrics, Tool, ToolsListResponse, ToolDetailResponse, UsageMetrics

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


@router.get("/{tool_id}")
async def get_tool(
  tool_id: int,
  tool_repository: ToolRepository = Depends(get_tool_repository)
):
    tool_model = tool_repository.get_tool(tool_id)
    tool = Tool.model_validate(tool_model)

    usage_metrics = UsageMetrics(
        last_30_days=SessionMetrics(
            total_sessions=0,
            avg_session_minutes=0
        )
    )
    
    total_monthly_cost = 0

    response = ToolDetailResponse(
        **tool.model_dump(),
        total_monthly_cost=total_monthly_cost,
        usage_metrics=usage_metrics
    )
    return response
