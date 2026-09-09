"""
AI配置API路由 - v3
参考 NewArcReel 的设计，使用 Provider Registry 系统
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import httpx
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.encryption import encrypt_text
from app.models.user import User
from app.models.ai_config import AiConfig
from app.schemas.ai_config import (
    AiConfigCreate,
    AiConfigResponse,
    AiConfigListResponse,
    FetchModelsRequest,
    FetchModelsResponse,
    ModelInfo,
    ProviderSummary,
    ProvidersListResponse
)
from app.config.provider_registry import (
    PROVIDER_REGISTRY,
    get_provider_meta,
    list_providers,
    list_provider_models
)

router = APIRouter()


def _to_response(config: AiConfig) -> AiConfigResponse:
    return AiConfigResponse(
        id=config.id,
        config_type=config.config_type,
        name=config.name,
        provider=config.provider,
        model=config.model_name,
        base_url=config.api_base_url,
        temperature=float(config.temperature) if config.temperature is not None else 0.7,
        max_tokens=config.max_tokens,
        is_active=config.is_default,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


@router.get("/providers", response_model=ProvidersListResponse)
async def get_providers():
    """获取所有支持的AI供应商列表（不需要认证）"""
    providers_list = []

    for provider_meta in list_providers():
        providers_list.append(ProviderSummary(
            id=provider_meta.id,
            display_name=provider_meta.display_name,
            description=provider_meta.description,
            required_keys=provider_meta.required_keys,
            optional_keys=provider_meta.optional_keys,
            default_base_url=provider_meta.default_base_url,
            model_count=len(provider_meta.models)
        ))

    return ProvidersListResponse(providers=providers_list)


@router.post("/actions/fetch-models", response_model=FetchModelsResponse)
@router.post("/models/fetch", response_model=FetchModelsResponse, include_in_schema=False)
@router.post("/fetch-models", response_model=FetchModelsResponse, include_in_schema=False)
async def fetch_models(
    request: FetchModelsRequest
):
    """根据供应商获取可用的模型列表（不需要认证）

    优先从供应商发现模型；失败时回退到 Registry，保证设置页仍可选择模型。
    """
    print(f"\n========== Fetch Models Request ==========")
    print(f"Provider: {request.provider}")
    print(f"Base URL: {request.baseUrl}")
    print(f"==========================================\n")

    # 从 Registry 获取供应商信息
    provider_meta = get_provider_meta(request.provider)

    if not provider_meta:
        # 如果不是预定义供应商，尝试调用 OpenAI 兼容 API
        return await _fetch_custom_provider_models(request)

    try:
        return await _discover_provider_models(request, provider_meta)
    except (httpx.HTTPError, ValueError) as exc:
        models = _registry_models(provider_meta)
        return FetchModelsResponse(
            models=models,
            source="registry",
            warning=f"在线模型发现失败，已显示内置模型：{str(exc)}",
        )


def _registry_models(provider_meta) -> List[ModelInfo]:
    return [
        ModelInfo(id=item.id, name=item.name, description=item.description)
        for item in provider_meta.models.values()
    ]


def _models_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    return f"{normalized}/models" if normalized.endswith("/v1") else f"{normalized}/v1/models"


async def _discover_provider_models(request: FetchModelsRequest, provider_meta) -> FetchModelsResponse:
    base_url = request.baseUrl or provider_meta.default_base_url
    if not base_url:
        raise ValueError("缺少 Base URL")

    headers = {"Accept": "application/json"}
    if provider_meta.discovery_format == "anthropic":
        headers.update({
            "x-api-key": request.apiKey,
            "anthropic-version": "2023-06-01",
        })
    else:
        headers["Authorization"] = f"Bearer {request.apiKey}"

    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        response = await client.get(_models_url(base_url), headers=headers)
        response.raise_for_status()
        payload = response.json()

    discovered = []
    for item in payload.get("data", []):
        model_id = item.get("id")
        if model_id:
            discovered.append(ModelInfo(
                id=model_id,
                name=item.get("display_name") or model_id,
                description="供应商在线返回的可用模型",
            ))
    if not discovered:
        raise ValueError("供应商响应中没有模型")
    discovered.sort(key=lambda item: item.id)
    return FetchModelsResponse(models=discovered, source="provider")


async def _fetch_custom_provider_models(request: FetchModelsRequest) -> FetchModelsResponse:
    """尝试从自定义供应商的 OpenAI 兼容 API 获取模型列表"""
    try:
        base_url = request.baseUrl or "http://localhost:8000"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                _models_url(base_url),
                headers={"Authorization": f"Bearer {request.apiKey}"},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                models: List[ModelInfo] = []

                for model in data.get("data", []):
                    models.append(ModelInfo(
                        id=model["id"],
                        name=model.get("id"),
                        description=f"自定义模型: {model.get('id')}"
                    ))

                if not models:
                    raise ValueError("供应商响应中没有模型")
                return FetchModelsResponse(models=models, source="provider")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"API 返回错误: {response.status_code}"
                )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="请求超时，请检查网络连接和 Base URL"
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"网络请求失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法自动获取模型列表: {str(e)}。请检查 API Key 和 Base URL 是否正确"
        )


@router.get("", response_model=AiConfigListResponse)
async def list_ai_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的AI配置列表（不返回api_key）"""
    result = await db.execute(
        select(AiConfig)
        .where(AiConfig.user_id == current_user.id)
        .order_by(AiConfig.created_at.desc())
    )
    configs = result.scalars().all()
    return {"configs": [_to_response(c) for c in configs]}


@router.post("", response_model=AiConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_config(
    config_data: AiConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """新建AI配置"""
    if config_data.activate:
        await db.execute(
            update(AiConfig)
            .where(
                AiConfig.user_id == current_user.id,
                AiConfig.config_type == config_data.config_type,
            )
            .values(is_default=False)
        )

    new_config = AiConfig(
        user_id=current_user.id,
        config_type=config_data.config_type,
        name=config_data.name,
        provider=config_data.provider,
        model_name=config_data.model,
        api_key=encrypt_text(config_data.apiKey),
        api_base_url=config_data.baseUrl,
        temperature=str(config_data.temperature),
        max_tokens=config_data.maxTokens,
        is_default=config_data.activate,
    )
    db.add(new_config)
    await db.commit()
    await db.refresh(new_config)
    return _to_response(new_config)


@router.post("/{config_id}/activate", response_model=AiConfigResponse)
async def activate_ai_config(
    config_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AiConfig).where(
            AiConfig.id == config_id,
            AiConfig.user_id == current_user.id,
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="AI config not found")
    await db.execute(
        update(AiConfig)
        .where(
            AiConfig.user_id == current_user.id,
            AiConfig.config_type == config.config_type,
        )
        .values(is_default=False)
    )
    config.is_default = True
    await db.commit()
    await db.refresh(config)
    return _to_response(config)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_config(
    config_id: int = Path(..., ge=1, description="配置ID"),  # 使用Path约束，必须>=1
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除AI配置"""
    result = await db.execute(
        select(AiConfig).where(
            AiConfig.id == config_id,
            AiConfig.user_id == current_user.id
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI config not found"
        )

    await db.delete(config)
    await db.commit()
    return None
