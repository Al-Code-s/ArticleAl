"""
文档Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.document import DocumentType, DocumentStatus


class DocumentBase(BaseModel):
    """文档基础Schema"""
    title: str = Field(..., max_length=500)
    type: DocumentType
    content: Optional[str] = None
    status: Optional[DocumentStatus] = DocumentStatus.DRAFT


class DocumentCreate(DocumentBase):
    """文档创建Schema"""
    project_id: int


class DocumentUpdate(BaseModel):
    """文档更新Schema"""
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    status: Optional[DocumentStatus] = None


class DocumentResponse(DocumentBase):
    """文档响应Schema"""
    id: int
    user_id: int
    project_id: int
    word_count: int
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentGenerateRequest(BaseModel):
    """文档生成请求Schema"""
    project_id: int = Field(..., description="项目ID")
    document_type: DocumentType = Field(..., description="文档类型")
    requirements: Optional[str] = Field(None, description="额外要求")


class DocumentListResponse(BaseModel):
    """文档列表响应Schema"""
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int
