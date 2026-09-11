"""
AI配置Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AiConfigCreate(BaseModel):
    """AI配置创建Schema"""
    config_type: str = Field(..., pattern="^(content_generation|agent)$")  # 配置类型
    name: str = Field(..., max_length=100)
    provider: str = Field(..., max_length=50)
    model: str = Field(..., max_length=100)
    apiKey: str = Field(..., min_length=1)
    baseUrl: Optional[str] = Field(None, max_length=255)
    temperature: float = 0.7
    maxTokens: int = 4096
    streamEnabled: bool = True
    activate: bool = True

class AiConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    apiKey: Optional[str] = None
    baseUrl: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    maxTokens: Optional[int] = Field(None, ge=1)


class AiConfigResponse(BaseModel):
    """AI配置响应Schema（不包含api_key）"""
    id: int
    config_type: str  # 配置类型
    name: str
    provider: str
    model: str
    base_url: Optional[str] = None
    temperature: float
    max_tokens: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AiConfigListResponse(BaseModel):
    """AI配置列表响应Schema"""
    configs: List[AiConfigResponse]


class FetchModelsRequest(BaseModel):
    """获取模型列表请求Schema"""
    provider: str = Field(..., max_length=50)
    apiKey: str = Field(..., min_length=1)
    baseUrl: Optional[str] = Field(None, max_length=255)


class ModelInfo(BaseModel):
    """模型信息Schema"""
    id: str
    name: str
    description: Optional[str] = None


class FetchModelsResponse(BaseModel):
    """获取模型列表响应Schema"""
    models: List[ModelInfo]
    source: str = "registry"
    warning: Optional[str] = None


class ProviderSummary(BaseModel):
    """供应商摘要Schema"""
    id: str
    display_name: str
    description: str
    required_keys: List[str]
    optional_keys: List[str]
    default_base_url: Optional[str] = None
    model_count: int


class ProvidersListResponse(BaseModel):
    """供应商列表响应Schema"""
    providers: List[ProviderSummary]
