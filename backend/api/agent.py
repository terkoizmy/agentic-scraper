from fastapi import APIRouter, HTTPException, status
from loguru import logger

from agent.brain import run_agent
from agent.memory import _session_tool_calls
from db import postgres
from models.schemas import AgentAskRequest, AgentAskResponse, WebSearchRequest, WebSearchResponse

router = APIRouter()


@router.post("/ask", response_model=AgentAskResponse)
async def agent_ask(body: AgentAskRequest):
    """Chat with the MiniMax M2.7 agent via the ReAct reasoning loop."""
    logger.info("Agent request: '{}' (Session: {})", body.message[:50], body.session_id)
    try:
        answer, session_id, tool_calls = await run_agent(body.message, body.session_id)
    except Exception as exc:
        logger.exception("Agent execution failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent loop failed: {exc}",
        )

    call_dicts = [tc.model_dump() for tc in tool_calls]
    
    await postgres.save_agent_session(
        session_id=session_id,
        user_message=body.message,
        tool_calls=call_dicts,
        final_answer=answer,
    )

    return AgentAskResponse(answer=answer, tool_calls=tool_calls, session_id=session_id)


@router.post("/search", response_model=WebSearchResponse)
async def web_search_endpoint(body: WebSearchRequest):
    """Directly test the DuckDuckGo web search tool."""
    from agent.tool_registry import execute_web_search
    try:
        res = await execute_web_search({"query": body.query, "max_results": body.max_results})
        if "error" in res:
            raise HTTPException(status_code=500, detail=res["error"])
        return WebSearchResponse(query=res["query"], results=res["results"])
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web search failed: {exc}",
        )


@router.get("/status/{session_id}")
async def get_agent_status(session_id: str):
    """Return the list of tool calls currently executed/being executed in the session."""
    tools = _session_tool_calls.get(session_id, [])
    return {"status": "ok", "tools": tools}
