from fastapi import APIRouter, HTTPException, status
from loguru import logger

from agent.brain import run_agent
from db import postgres
from models.schemas import AgentAskRequest, AgentAskResponse

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
