"""Resolve a user's active AI configuration and build the matching SDK client."""
from dataclasses import dataclass
from typing import Optional

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import decrypt_text
from app.models.ai_config import AiConfig


@dataclass
class ActiveAIConfig:
    provider: str
    model: str
    api_key: str
    base_url: Optional[str]
    temperature: float
    max_tokens: int


async def get_active_ai_config(
    db: AsyncSession,
    user_id: int,
    config_type: str,
) -> Optional[ActiveAIConfig]:
    result = await db.execute(
        select(AiConfig)
        .where(
            AiConfig.user_id == user_id,
            AiConfig.config_type == config_type,
            AiConfig.is_default.is_(True),
        )
        .order_by(AiConfig.updated_at.desc())
        .limit(1)
    )
    config = result.scalar_one_or_none()
    if not config:
        return None
    return ActiveAIConfig(
        provider=config.provider,
        model=config.model_name,
        api_key=decrypt_text(config.api_key),
        base_url=config.api_base_url,
        temperature=float(config.temperature or 0.7),
        max_tokens=config.max_tokens or 4096,
    )


def build_anthropic_client(config: ActiveAIConfig) -> AsyncAnthropic:
    kwargs = {"api_key": config.api_key}
    if config.base_url:
        kwargs["base_url"] = config.base_url.rstrip("/")
    return AsyncAnthropic(**kwargs)


def build_openai_client(config: ActiveAIConfig) -> AsyncOpenAI:
    kwargs = {"api_key": config.api_key}
    if config.base_url:
        kwargs["base_url"] = config.base_url.rstrip("/")
    return AsyncOpenAI(**kwargs)
