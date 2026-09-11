"""Claude Agent SDK runtime with a safe compatibility fallback.

The SDK path owns a long-lived client per project session. The existing chat
service remains the fallback for installations that have not installed the SDK
or configured an Anthropic credential.
"""
from __future__ import annotations

import logging
from typing import Any, AsyncIterator

logger = logging.getLogger(__name__)

try:
    from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
except ImportError:  # pragma: no cover - exercised only in minimal installs
    ClaudeAgentOptions = None
    ClaudeSDKClient = None


class AgentRuntimeUnavailable(RuntimeError):
    pass


class ProjectAgentService:
    """One resumable Claude SDK session per project, with project-scoped tools."""

    def __init__(self, project_id: int, project_context: dict[str, Any], system_prompt: str):
        self.project_id = project_id
        self.project_context = project_context
        self.system_prompt = system_prompt
        self.client: Any = None

    async def start(self) -> None:
        if ClaudeSDKClient is None or ClaudeAgentOptions is None:
            raise AgentRuntimeUnavailable("claude-agent-sdk 未安装")
        options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            max_turns=20,
            # Tools are added as this runtime grows; all calls remain project scoped.
            allowed_tools=["Read", "Glob", "Grep"],
        )
        self.client = ClaudeSDKClient(options=options)
        await self.client.__aenter__()

    async def send(self, message: str) -> AsyncIterator[dict[str, Any]]:
        if self.client is None:
            raise AgentRuntimeUnavailable("Agent session 尚未启动")
        enriched = (
            f"当前项目上下文（只读事实）：{self.project_context}\n\n"
            f"用户任务：{message}"
        )
        await self.client.query(enriched)
        async for event in self.client.receive_response():
            yield self._normalize_event(event)

    async def close(self) -> None:
        if self.client is not None:
            await self.client.__aexit__(None, None, None)
            self.client = None

    @staticmethod
    def _normalize_event(event: Any) -> dict[str, Any]:
        if isinstance(event, dict):
            return event
        text = getattr(event, "text", None) or getattr(event, "content", None)
        return {"type": "message", "content": str(text or event)}
