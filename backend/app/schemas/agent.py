"""
智能体Schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.agent_session import SessionStatus
from app.models.agent_message import MessageRole


class AgentMessageCreate(BaseModel):
    """智能体消息创建Schema"""
    content: str = Field(..., min_length=1)


class AgentMessageResponse(BaseModel):
    """智能体消息响应Schema"""
    id: int
    session_id: int
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None
    tokens: int
    created_at: datetime

    class Config:
        from_attributes = True


class AgentSessionResponse(BaseModel):
    """智能体会话响应Schema"""
    id: int
    session_id: str
    status: SessionStatus
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    total_tokens: int
    total_messages: int
    started_at: datetime
    last_active_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentStatusResponse(BaseModel):
    """智能体状态响应Schema"""
    session_id: str
    status: SessionStatus
    is_running: bool
    message_count: int
    total_tokens: int
