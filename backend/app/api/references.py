"""
参考文献API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.reference import Reference
from app.schemas.reference import (
    ReferenceCreate,
    ReferenceUpdate,
    ReferenceResponse,
    ReferenceListResponse,
    ReferenceSearchRequest,
)
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/search", response_model=list[ReferenceResponse])
async def search_references(
    request: ReferenceSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    搜索参考文献

    通过知网或其他学术数据库搜索文献
    """
    # 使用 AI 服务搜索文献
    references_data = await ai_service.search_references(
        keyword=request.keyword,
        max_results=request.max_results
    )

    # 如果提供了project_id，保存到数据库
    references = []
    if request.project_id:
        for ref_data in references_data:
            new_ref = Reference(
                user_id=current_user.id,
                project_id=request.project_id,
                **ref_data
            )
            db.add(new_ref)
            references.append(new_ref)

        await db.commit()
        for ref in references:
            await db.refresh(ref)
    else:
        # 只返回搜索结果，不保存
        references = [Reference(**data) for data in references_data]

    return references


@router.post("", response_model=ReferenceResponse)
async def create_reference(
    reference_data: ReferenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """手动添加参考文献"""
    new_reference = Reference(
        user_id=current_user.id,
        **reference_data.model_dump()
    )

    db.add(new_reference)
    await db.commit()
    await db.refresh(new_reference)

    return new_reference


@router.get("", response_model=ReferenceListResponse)
async def list_references(
    project_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取参考文献列表"""
    query = select(Reference).where(Reference.user_id == current_user.id)

    if project_id:
        query = query.where(Reference.project_id == project_id)

    # 计算总数
    count_result = await db.execute(
        select(func.count(Reference.id)).select_from(query.subquery())
    )
    total = count_result.scalar()

    # 获取分页数据
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(Reference.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    references = result.scalars().all()

    return {
        "items": references,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{reference_id}", response_model=ReferenceResponse)
async def get_reference(
    reference_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取参考文献详情"""
    result = await db.execute(
        select(Reference).where(
            Reference.id == reference_id,
            Reference.user_id == current_user.id
        )
    )
    reference = result.scalar_one_or_none()

    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found"
        )

    return reference


@router.put("/{reference_id}", response_model=ReferenceResponse)
async def update_reference(
    reference_id: int,
    reference_data: ReferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新参考文献"""
    result = await db.execute(
        select(Reference).where(
            Reference.id == reference_id,
            Reference.user_id == current_user.id
        )
    )
    reference = result.scalar_one_or_none()

    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found"
        )

    # 更新字段
    update_data = reference_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reference, field, value)

    await db.commit()
    await db.refresh(reference)
    return reference


@router.delete("/{reference_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reference(
    reference_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除参考文献"""
    result = await db.execute(
        select(Reference).where(
            Reference.id == reference_id,
            Reference.user_id == current_user.id
        )
    )
    reference = result.scalar_one_or_none()

    if not reference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference not found"
        )

    await db.delete(reference)
    await db.commit()
    return None
