from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from core import settings_state

router = APIRouter(prefix="/api/settings", tags=["Settings"])


class AgentSettingsPatch(BaseModel):
    thinking_enabled: Optional[bool] = None
    thinking_max_tokens: Optional[int] = None


class AgentSettingsResponse(BaseModel):
    thinking_enabled: bool
    thinking_max_tokens: int


@router.get("/agent", response_model=AgentSettingsResponse)
async def get_agent_settings():
    return {
        "thinking_enabled": settings_state.get_thinking_enabled(),
        "thinking_max_tokens": settings_state.get_thinking_max_tokens(),
    }


@router.patch("/agent")
async def patch_agent_settings(patch: AgentSettingsPatch):
    if patch.thinking_enabled is not None:
        settings_state.set_thinking_enabled(patch.thinking_enabled)
    if patch.thinking_max_tokens is not None:
        settings_state.set_thinking_max_tokens(patch.thinking_max_tokens)
    return {"status": "ok"}