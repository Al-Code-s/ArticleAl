"""
项目API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建项目"""
    new_project = Project(
        user_id=current_user.id,
        title=project_data.title,
        description=project_data.description,
        major=project_data.major,
        education_level=project_data.education_level,
        paper_type=project_data.paper_type,
        word_count=project_data.word_count,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目列表"""
    # 计算总数
    count_result = await db.execute(
        select(func.count(Project.id)).where(Project.user_id == current_user.id)
    )
    total = count_result.scalar()

    # 获取分页数据
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    projects = result.scalars().all()

    return {
        "items": projects,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目详情"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新项目"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # 更新字段
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除项目"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Explicitly remove children so old databases do not trigger ORM relationship
    # loads against columns that were added in newer model versions.
    params = {"project_id": project_id}
    for table in ("topics", "outlines", "documents", "paper_sections", "export_records"):
        await db.execute(text(f"DELETE FROM {table} WHERE project_id = :project_id"), params)
    await db.execute(text('DELETE FROM "references" WHERE project_id = :project_id'), params)
    # Agent messages reference sessions, so remove them before their session.
    await db.execute(text("DELETE FROM agent_messages WHERE session_id IN (SELECT id FROM agent_sessions WHERE project_id = :project_id)"), params)
    await db.execute(text("DELETE FROM agent_sessions WHERE project_id = :project_id"), params)
    await db.execute(text("DELETE FROM projects WHERE id = :project_id AND user_id = :user_id"), {
        "project_id": project_id,
        "user_id": current_user.id,
    })
    await db.commit()
    return None
