"""
选题Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import json


class TopicBase(BaseModel):
    """选题基础Schema"""
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    major: str = Field(..., max_length=100)
    education_level: str = Field(..., max_length=50)
    paper_type: str = Field(..., max_length=50)
    keywords: Optional[List[str]] = None
    difficulty: Optional[str] = None

    @field_validator("keywords", mode="before")
    @classmethod
    def parse_keywords(cls, value):
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else [value]
            except json.JSONDecodeError:
                return [value]
        return value


class TopicCreate(TopicBase):
    """选题创建Schema"""
    project_id: Optional[int] = None


class TopicUpdate(BaseModel):
    """选题更新Schema"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    difficulty: Optional[str] = None
    is_selected: Optional[bool] = None


class TopicResponse(TopicBase):
    """选题响应Schema"""
    id: int
    user_id: int
    project_id: Optional[int] = None
    is_selected: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TopicGenerateRequest(BaseModel):
    """选题生成请求Schema"""
    project_id: Optional[int] = Field(None, description="项目ID")
    major: str = Field(..., max_length=100, description="专业")
    education_level: str = Field(..., max_length=50, description="学历层次：成人教育、专科、本科")
    paper_type: str = Field(..., max_length=50, description="毕业论文类型")
    count: int = Field(3, ge=1, le=20, description="生成数量")
    keywords: Optional[List[str]] = Field(None, description="关键词")

    @field_validator("education_level")
    @classmethod
    def validate_education_level(cls, value: str) -> str:
        allowed = {"成人教育", "专科", "本科"}
        if value not in allowed:
            raise ValueError("学历必须是成人教育、专科或本科")
        return value

    @field_validator("paper_type")
    @classmethod
    def validate_paper_type(cls, value: str) -> str:
        allowed = {"论述性论文", "研究性论文", "实证研究论文", "调查研究论文", "案例研究论文", "设计实践论文"}
        if value not in allowed:
            raise ValueError("论文类型不受支持，请选择专业的毕业论文类型")
        return value


class TopicListResponse(BaseModel):
    """选题列表响应Schema"""
    items: List[TopicResponse]
    total: int
    page: int
    page_size: int
