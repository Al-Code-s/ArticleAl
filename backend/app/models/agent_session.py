"""
智能体会话模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class SessionStatus(str, enum.Enum):
    """会话状态"""
    ACTIVE = "active"
    IDLE = "idle"
    STOPPED = "stopped"
    ERROR = "error"


class AgentSession(Base):
    """智能体会话表"""
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=True)  # 关联项目（通过反向引用）
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE)
    context = Column(JSON)  # 会话上下文
    session_metadata = Column(JSON)  # 元数据（重命名以避免冲突）
    total_tokens = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # 关系
    project = relationship("Project", back_populates="agent_session", foreign_keys="Project.agent_session_id")
    messages = relationship("AgentMessage", back_populates="session", cascade="all, delete-orphan")
