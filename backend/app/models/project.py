"""
项目模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    """项目状态"""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AgentStatus(str, enum.Enum):
    """智能体状态"""
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class Project(Base):
    """项目表"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    major = Column(String(100), nullable=False)
    education_level = Column(String(50), nullable=False)
    paper_type = Column(String(50), nullable=False)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.CREATED)

    # 智能体相关
    agent_session_id = Column(Integer, ForeignKey("agent_sessions.id", ondelete="SET NULL"), nullable=True)
    agent_status = Column(SQLEnum(AgentStatus), default=AgentStatus.IDLE)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="projects")
    agent_session = relationship("AgentSession", back_populates="project", foreign_keys=[agent_session_id])
    outline = relationship("Outline", back_populates="project", uselist=False, cascade="all, delete-orphan")
    references = relationship("Reference", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    paper_sections = relationship("PaperSection", back_populates="project", cascade="all, delete-orphan")
