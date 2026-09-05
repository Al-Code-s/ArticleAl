"""
项目Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.project import ProjectStatus, AgentStatus


class ProjectBase(BaseModel):
    """项目基础Schema"""
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    major: str = Field(..., max_length=100)
    education_level: str = Field(..., max_length=50)
    paper_type: str = Field(..., max_length=50)


class ProjectCreate(ProjectBase):
    """项目创建Schema"""
    pass


class ProjectUpdate(BaseModel):
    """项目更新Schema"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    """项目响应Schema"""
    id: int
    user_id: int
    status: ProjectStatus
    agent_status: AgentStatus
    agent_session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """项目列表响应Schema"""
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int
