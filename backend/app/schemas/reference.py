"""
参考文献Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ReferenceBase(BaseModel):
    """参考文献基础Schema"""
    title: str
    authors: List[str]
    journal: Optional[str] = None
    year: Optional[int] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None


class ReferenceCreate(ReferenceBase):
    """参考文献创建Schema"""
    cnki_url: Optional[str] = None
    citation_format: Optional[str] = None


class ReferenceUpdate(BaseModel):
    """参考文献更新Schema"""
    is_selected: Optional[bool] = None


class ReferenceResponse(ReferenceBase):
    """参考文献响应Schema"""
    id: int
    project_id: int
    cnki_url: Optional[str] = None
    citation_count: int
    citation_format: Optional[str] = None
    is_selected: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReferenceSearchRequest(BaseModel):
    """参考文献搜索请求Schema"""
    keywords: List[str] = Field(..., min_items=1, description="搜索关键词")
    limit: int = Field(20, ge=1, le=100, description="返回数量")
    year_from: Optional[int] = Field(None, description="起始年份")
    year_to: Optional[int] = Field(None, description="结束年份")


class ReferenceListResponse(BaseModel):
    """参考文献列表响应Schema"""
    items: List[ReferenceResponse]
    total: int
