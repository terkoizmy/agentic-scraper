import uuid
from typing import Any, Dict, List, Optional


_active_sessions: Dict[str, List[Dict[str, Any]]] = {}


def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, List[Dict[str, Any]]]:
    """Retrieve an existing session or initialize a fresh context."""
    if not session_id or session_id not in _active_sessions:
        session_id = str(uuid.uuid4())
        _active_sessions[session_id] = [
            {
                "role": "system",
                "content": (
                    "Anda adalah agen pintar yang memiliki kemampuan scraping web, "
                    "crawling dokumentasi, dan query data (RAG). Tugas Anda adalah "
                    "membantu pengguna mencari informasi dari website atau database lokal "
                    "dengan menggunakan tool yang tersedia. Gunakan tool jika konteks belum cukup."
                ),
            }
        ]
    return session_id, _active_sessions[session_id].copy()


def format_user_message(message: str) -> Dict[str, Any]:
    """Structure a user message for the dialogue context."""
    return {"role": "user", "content": message}


def format_assistant_response(
    content: Optional[str] = None, tool_calls: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Structure an assistant response string or tool calls request."""
    msg: Dict[str, Any] = {"role": "assistant", "content": content or ""}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return msg


def format_tool_message(tool_call_id: str, tool_name: str, result_content: str) -> Dict[str, Any]:
    """Structure a tool execution result to be fed back to the LLM."""
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": tool_name,
        "content": result_content,
    }


def add_message(session_id: str, message: Dict[str, Any]) -> None:
    """Append a formatted arbitrary message block to a session state."""
    if session_id in _active_sessions:
        _active_sessions[session_id].append(message)


def clear_session(session_id: str) -> None:
    """Wipe an active session."""
    if session_id in _active_sessions:
        del _active_sessions[session_id]
