"""Runtime settings state - overrides config defaults at runtime."""

from typing import Optional

_thinking_enabled: Optional[bool] = None
_thinking_max_tokens: Optional[int] = None


def get_thinking_enabled() -> bool:
    """Get thinking setting (runtime override or config default)."""
    from core.config import settings
    return _thinking_enabled if _thinking_enabled is not None else settings.agent_thinking_enabled


def set_thinking_enabled(value: bool) -> None:
    global _thinking_enabled
    _thinking_enabled = value


def get_thinking_max_tokens() -> int:
    """Get thinking max tokens (runtime override or config default)."""
    from core.config import settings
    return _thinking_max_tokens if _thinking_max_tokens is not None else settings.agent_thinking_max_tokens


def set_thinking_max_tokens(value: int) -> None:
    global _thinking_max_tokens
    _thinking_max_tokens = value