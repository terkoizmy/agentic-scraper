import json
import uuid
from typing import Any

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from agent.memory import (
    add_message,
    format_assistant_response,
    format_tool_message,
    format_user_message,
    get_or_create_session,
    has_rag_query_in_session,
    track_tool_call,
)
from agent.tool_registry import dispatch_tool_call
from agent.tools import TOOLS
from core.config import settings
from core.exceptions import AgentError
from core import settings_state
from models.schemas import ToolCallRecord


LLM_RETRY_ATTEMPTS = 3
LLM_RETRY_MIN_WAIT = 2
LLM_RETRY_MAX_WAIT = 10


@retry(
    stop=stop_after_attempt(LLM_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=LLM_RETRY_MIN_WAIT, max=LLM_RETRY_MAX_WAIT),
    retry=retry_if_exception_type((httpx.ReadTimeout, httpx.HTTPStatusError)),
    reraise=True,
)
async def _call_minimax(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Call MiniMax Chat API with tools using httpx."""
    is_minimax = "minimax.chat" in settings.minimax_base_url

    if is_minimax and (not settings.minimax_api_key or not settings.minimax_group_id):
        raise AgentError("MINIMAX_API_KEY and MINIMAX_GROUP_ID required in .env for official MiniMax API")

    if is_minimax:
        url = f"{settings.minimax_base_url.rstrip('/')}/text/chatcompletion_v2"
    else:
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

    if settings_state.get_thinking_enabled():
        payload["thinking"] = {
            "type": "enabled",
            "max_tokens": settings_state.get_thinking_max_tokens(),
        }

    async with httpx.AsyncClient(timeout=180.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


async def run_agent(message: str, session_id: str | None = None) -> tuple[str, str, list[ToolCallRecord]]:
    """Execute ReAct loop interpreting user intent with tools."""
    sid, messages_copy = get_or_create_session(session_id)

    user_msg = format_user_message(message)
    messages_copy.append(user_msg)
    await add_message(sid, user_msg)

    executed_records: list[ToolCallRecord] = []

    for iteration in range(settings.agent_max_iterations):
        logger.info("Agent ReAct loop iteration {}/{}", iteration + 1, settings.agent_max_iterations)
        
        try:
            res = await _call_minimax(messages_copy)
        except (httpx.ReadTimeout, httpx.HTTPStatusError) as exc:
            logger.error("LLM call failed after {} retries: {}", LLM_RETRY_ATTEMPTS, exc)
            error_msg = "Maaf, terjadi kesalahan saat menghubungi layanan AI. Silakan coba lagi dalam beberapa saat."
            return error_msg, sid, executed_records
        except Exception as exc:
            logger.error("Unexpected error calling LLM: {}", exc)
            error_msg = "Maaf, terjadi kesalahan yang tidak terduga. Silakan coba lagi."
            return error_msg, sid, executed_records

        choices = res.get("choices", [])
        if not choices:
            raise AgentError(f"No choices returned by MiniMax: {res}")

        choice = choices[0]
        msg_out = choice.get("message", {})
        content = msg_out.get("content")
        tool_calls = msg_out.get("tool_calls", [])

        asst_msg = format_assistant_response(content, tool_calls)
        messages_copy.append(asst_msg)
        await add_message(sid, asst_msg)

        if not tool_calls:
            logger.info("Agent concluded with a final answer in {} iterations", iteration + 1)
            return content or "No answer provided.", sid, executed_records

        for t_call in tool_calls:
            t_id = t_call.get("id", str(uuid.uuid4()))
            t_func = t_call.get("function", {})
            t_name = t_func.get("name")
            t_args = t_func.get("arguments", "{}")

            track_tool_call(sid, t_name)

            t_result = await dispatch_tool_call(t_name, t_args, sid)
            t_result_str = json.dumps(t_result, default=str)

            try:
                parsed_args = json.loads(t_args)
            except json.JSONDecodeError:
                parsed_args = {}

            record = ToolCallRecord(tool=t_name, args=parsed_args, result=t_result)
            executed_records.append(record)

            tool_msg_form = format_tool_message(t_id, t_name, t_result_str)
            messages_copy.append(tool_msg_form)
            await add_message(sid, tool_msg_form)

    logger.warning("Agent exhausted max {} iterations.", settings.agent_max_iterations)
    msg = "Maaf, saya mencapai batas iterasi pemikiran. Mohon spesifikasikan lebih lanjut."
    return msg, sid, executed_records
