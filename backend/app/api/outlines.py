"""
大纲API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.outline import Outline
from app.models.project import Project
from app.schemas.outline import (
    OutlineCreate,
    OutlineUpdate,
    OutlineResponse,
    OutlineListResponse,
    OutlineGenerateRequest,
)
from app.services.ai_service import ai_service
from app.services.skill_service import resolve_skill, with_context
from app.services.ai_runtime import get_active_ai_config

router = APIRouter()


@router.post("/generate", response_model=OutlineResponse)
async def generate_outline(
    request: OutlineGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    生成论文大纲

    根据选题和要求生成论文大纲结构
    """
    # 验证项目是否存在
    project_result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.user_id == current_user.id
        )
    )
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 使用 AI 服务生成大纲
    ai_config = await get_active_ai_config(db, current_user.id, "content_generation")
    skill_instructions = with_context(await resolve_skill(db, current_user.id, "outline"), {
        "论文标题": request.topic_title, "专业": project.major,
        "学历层次": project.education_level, "论文类型": project.paper_type,
        "额外要求": request.requirements,
    })
    outline_content = await ai_service.generate_outline(
        topic_title=request.topic_title,
        major=project.major,
        education_level=project.education_level,
        paper_type=project.paper_type,
        requirements=request.requirements,
        ai_config=ai_config,
        skill_instructions=skill_instructions,
    )

    # 创建大纲
    new_outline = Outline(
        user_id=current_user.id,
        project_id=request.project_id,
        title=request.topic_title,
        content=outline_content,
        version=1
    )

    db.add(new_outline)
    await db.commit()
    await db.refresh(new_outline)

    return new_outline


@router.get("", response_model=OutlineListResponse)
async def list_outlines(
    project_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取大纲列表"""
    query = select(Outline).where(Outline.user_id == current_user.id)

    if project_id:
        query = query.where(Outline.project_id == project_id)

    # 计算总数
    count_result = await db.execute(
        select(func.count(Outline.id)).select_from(query.subquery())
    )
    total = count_result.scalar()

    # 获取分页数据
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(Outline.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    outlines = result.scalars().all()

    return {
        "items": outlines,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{outline_id}", response_model=OutlineResponse)
async def get_outline(
    outline_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取大纲详情"""
    result = await db.execute(
        select(Outline).where(
            Outline.id == outline_id,
            Outline.user_id == current_user.id
        )
    )
    outline = result.scalar_one_or_none()

    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outline not found"
        )

    return outline


@router.put("/{outline_id}", response_model=OutlineResponse)
async def update_outline(
    outline_id: int,
    outline_data: OutlineUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新大纲"""
    result = await db.execute(
        select(Outline).where(
            Outline.id == outline_id,
            Outline.user_id == current_user.id
        )
    )
    outline = result.scalar_one_or_none()

    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outline not found"
        )

    # 更新字段
    update_data = outline_data.model_dump(exclude_unset=True)

    # 如果更新了内容，增加版本号
    if "content" in update_data:
        outline.version += 1

    for field, value in update_data.items():
        setattr(outline, field, value)

    await db.commit()
    await db.refresh(outline)
    return outline


@router.delete("/{outline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outline(
    outline_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除大纲"""
    result = await db.execute(
        select(Outline).where(
            Outline.id == outline_id,
            Outline.user_id == current_user.id
        )
    )
    outline = result.scalar_one_or_none()

    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outline not found"
        )

    await db.delete(outline)
    await db.commit()
    return None
