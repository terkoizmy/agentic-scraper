import json
import uuid
from typing import Any

import httpx
from loguru import logger

from agent.memory import (
    add_message,
    format_assistant_response,
    format_tool_message,
    format_user_message,
    get_or_create_session,
)
from agent.tool_registry import dispatch_tool_call
from agent.tools import TOOLS
from core.config import settings
from core.exceptions import AgentError
from models.schemas import ToolCallRecord


async def _call_minimax(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Call MiniMax Chat API with tools using httpx."""
    # Auto-detect if using official MiniMax API vs Ollama/OpenAI-compatible local server
    is_minimax = "minimax.chat" in settings.minimax_base_url

    if is_minimax and (not settings.minimax_api_key or not settings.minimax_group_id):
        raise AgentError("MINIMAX_API_KEY and MINIMAX_GROUP_ID required in .env for official MiniMax API")

    if is_minimax:
        url = f"{settings.minimax_base_url.rstrip('/')}/text/chatcompletion_v2"
    else:
        # Fallback to standard OpenAI compatibility format (used by Ollama)
        url = f"{settings.minimax_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.minimax_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.minimax_model,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "temperature": settings.agent_temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        msg = f"HTTP Error calling MiniMax: {exc}"
        if isinstance(exc, httpx.HTTPStatusError):
            msg += f" Response: {exc.response.text}"
        logger.error(msg)
        raise AgentError(msg) from exc


async def run_agent(message: str, session_id: str | None = None) -> tuple[str, str, list[ToolCallRecord]]:
    """Execute ReAct loop interpreting user intent with tools."""
    sid, messages_copy = get_or_create_session(session_id)

    user_msg = format_user_message(message)
    messages_copy.append(user_msg)
    add_message(sid, user_msg)

    executed_records: list[ToolCallRecord] = []

    for iteration in range(settings.agent_max_iterations):
        logger.info("Agent ReAct loop iteration {}/{}", iteration + 1, settings.agent_max_iterations)
        
        res = await _call_minimax(messages_copy)
        choices = res.get("choices", [])
        if not choices:
            raise AgentError(f"No choices returned by MiniMax: {res}")

        choice = choices[0]
        msg_out = choice.get("message", {})
        content = msg_out.get("content")
        tool_calls = msg_out.get("tool_calls", [])

        asst_msg = format_assistant_response(content, tool_calls)
        messages_copy.append(asst_msg)
        add_message(sid, asst_msg)

        if not tool_calls:
            logger.info("Agent concluded with a final answer in {} iterations", iteration + 1)
            return content or "No answer provided.", sid, executed_records

        for t_call in tool_calls:
            t_id = t_call.get("id", str(uuid.uuid4()))
            t_func = t_call.get("function", {})
            t_name = t_func.get("name")
            t_args = t_func.get("arguments", "{}")

            t_result = await dispatch_tool_call(t_name, t_args)
            t_result_str = json.dumps(t_result)

            try:
                parsed_args = json.loads(t_args)
            except json.JSONDecodeError:
                parsed_args = {}

            record = ToolCallRecord(tool=t_name, args=parsed_args, result=t_result)
            executed_records.append(record)

            tool_msg_form = format_tool_message(t_id, t_name, t_result_str)
            messages_copy.append(tool_msg_form)
            add_message(sid, tool_msg_form)

    logger.warning("Agent exhausted max {} iterations.", settings.agent_max_iterations)
    msg = "Maaf, saya mencapai batas iterasi pemikiran. Mohon spesifikasikan lebih lanjut."
    return msg, sid, executed_records
