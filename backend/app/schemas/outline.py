"""
大纲Schemas
"""
from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel, Field


class OutlineBase(BaseModel):
    """大纲基础Schema"""
    title: str = Field(..., max_length=500)
    content: Optional[Any] = None  # JSON 格式的大纲内容


class OutlineCreate(OutlineBase):
    """大纲创建Schema"""
    project_id: int


class OutlineUpdate(BaseModel):
    """大纲更新Schema"""
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[Any] = None


class OutlineResponse(OutlineBase):
    """大纲响应Schema"""
    id: int
    user_id: int
    project_id: int
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OutlineGenerateRequest(BaseModel):
    """大纲生成请求Schema"""
    project_id: int = Field(..., description="项目ID")
    topic_title: str = Field(..., description="选题标题")
    requirements: Optional[str] = Field(None, description="额外要求")


class OutlineListResponse(BaseModel):
    """大纲列表响应Schema"""
    items: List[OutlineResponse]
    total: int
    page: int
    page_size: int
