"""
选题API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import json
import re

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.topic import Topic
from app.schemas.topic import (
    TopicCreate,
    TopicUpdate,
    TopicResponse,
    TopicListResponse,
    TopicGenerateRequest,
)
from app.services.ai_service import ai_service
from app.services.skill_service import resolve_skill, with_context
from app.services.ai_runtime import get_active_ai_config

router = APIRouter()


@router.post("/generate", response_model=list[TopicResponse])
async def generate_topics(
    request: TopicGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    生成论文选题

    根据专业、学历、论文类型生成候选题目
    """
    # 使用 AI 服务生成选题
    ai_config = await get_active_ai_config(db, current_user.id, "content_generation")
    skill_instructions = with_context(await resolve_skill(db, current_user.id, "topics"), {
        "专业": request.major, "学历层次": request.education_level,
        "论文类型": request.paper_type, "关键词": request.keywords, "生成数量": request.count,
    })
    try:
        generated_topics = await ai_service.generate_topics(
            major=request.major,
            education_level=request.education_level,
            paper_type=request.paper_type,
            keywords=request.keywords,
            count=request.count,
            ai_config=ai_config,
            skill_instructions=skill_instructions,
        )
    except Exception:
        generated_topics = ai_service._generate_mock_topics(
            request.major, request.education_level, request.paper_type, request.count
        )

    # 保存生成的选题到数据库；对模型输出做容错，避免一条格式异常导致整批失败。
    # AI 返回数量不足或返回占位标题时，用同样输入生成的本地候选补齐。
    fallback_topics = ai_service._generate_mock_topics(
        request.major, request.education_level, request.paper_type, request.count
    )
    candidate_topics = list(generated_topics) if isinstance(generated_topics, list) else []
    candidate_topics.extend(fallback_topics)
    topics = []
    seen_titles = set()
    for topic_data in candidate_topics:
        if not isinstance(topic_data, dict):
            continue
        raw_title = topic_data.get("title")
        if not isinstance(raw_title, str):
            continue
        title = raw_title.strip()
        if not title:
            continue
        if (
            re.fullmatch(r"基于.+的\d+号研究课题", title)
            or re.fullmatch(r".+毕业论文选题[（(]\d+[）)]", title)
        ):
            continue
        title_key = title[:500]
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        description = str(topic_data.get("description") or "围绕该选题开展毕业论文研究。").strip()
        keywords = topic_data.get("keywords") or []
        if isinstance(keywords, str):
            keywords = [keywords]
        if not isinstance(keywords, list):
            keywords = []
        new_topic = Topic(
            user_id=current_user.id,
            project_id=request.project_id,
            title=title[:500],
            description=description,
            major=request.major,
            education_level=request.education_level,
            paper_type=request.paper_type,
            keywords=json.dumps(keywords, ensure_ascii=False),
        )
        db.add(new_topic)
        topics.append(new_topic)
        if len(topics) >= request.count:
            break

    if not topics:
        raise HTTPException(status_code=502, detail="AI 未返回有效的论文题目，请重试")

    try:
        await db.commit()
        for topic in topics:
            await db.refresh(topic)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"保存生成题目失败：{exc}") from exc

    return topics


@router.get("", response_model=TopicListResponse)
async def list_topics(
    project_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取选题列表"""
    query = select(Topic).where(Topic.user_id == current_user.id)

    if project_id:
        query = query.where(Topic.project_id == project_id)

    # 计算总数
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()

    # 获取分页数据
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(Topic.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    topics = result.scalars().all()

    return {
        "items": topics,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取选题详情"""
    result = await db.execute(
        select(Topic).where(
            Topic.id == topic_id,
            Topic.user_id == current_user.id
        )
    )
    topic = result.scalar_one_or_none()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    return topic


@router.post("/{topic_id}/select", response_model=TopicResponse)
async def select_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    选择该选题

    将选题标记为已选择，并可能更新关联项目的状态
    """
    result = await db.execute(
        select(Topic).where(
            Topic.id == topic_id,
            Topic.user_id == current_user.id
        )
    )
    topic = result.scalar_one_or_none()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    # 如果有项目ID，取消该项目的其他选题
    if topic.project_id:
        await db.execute(
            Topic.__table__.update()
            .where(Topic.project_id == topic.project_id, Topic.id != topic_id)
            .values(is_selected=False)
        )

    topic.is_selected = True
    await db.commit()
    await db.refresh(topic)

    return topic


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新选题"""
    result = await db.execute(
        select(Topic).where(
            Topic.id == topic_id,
            Topic.user_id == current_user.id
        )
    )
    topic = result.scalar_one_or_none()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    # 更新字段
    update_data = topic_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(topic, field, value)

    await db.commit()
    await db.refresh(topic)
    return topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除选题"""
    result = await db.execute(
        select(Topic).where(
            Topic.id == topic_id,
            Topic.user_id == current_user.id
        )
    )
    topic = result.scalar_one_or_none()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    await db.delete(topic)
    await db.commit()
    return None
