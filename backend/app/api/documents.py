"""
文档API路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentType, DocumentStatus
from app.models.project import Project
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentGenerateRequest,
)
from app.services.ai_service import ai_service
from app.services.ai_runtime import get_active_ai_config

router = APIRouter()


@router.post("/generate", response_model=DocumentResponse)
async def generate_document(
    request: DocumentGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    生成文档

    根据项目信息和文档类型生成相应的文档内容
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

    # 获取项目的大纲和参考文献（如果有）
    from app.models.outline import Outline
    from app.models.reference import Reference

    outline_result = await db.execute(
        select(Outline).where(
            Outline.project_id == request.project_id
        ).order_by(Outline.created_at.desc()).limit(1)
    )
    outline = outline_result.scalar_one_or_none()

    references_result = await db.execute(
        select(Reference).where(
            Reference.project_id == request.project_id
        )
    )
    references = references_result.scalars().all()

    # 使用 AI 服务生成文档内容
    ai_config = await get_active_ai_config(db, current_user.id, "content_generation")
    document_content = await ai_service.generate_document(
        document_type=request.document_type.value,
        topic_title=project.title,
        outline=outline.content if outline else None,
        references=[{
            "title": ref.title,
            "authors": ref.authors,
            "year": ref.year,
            "publication": ref.publication
        } for ref in references],
        requirements=request.requirements,
        ai_config=ai_config,
    )

    document_titles = {
        DocumentType.PROPOSAL: "开题报告",
        DocumentType.LITERATURE_REVIEW: "文献综述",
        DocumentType.THESIS: "论文正文",
        DocumentType.ASSIGNMENT: "任务书",
    }

    # 创建文档
    new_document = Document(
        user_id=current_user.id,
        project_id=request.project_id,
        title=f"{project.title} - {document_titles.get(request.document_type, '文档')}",
        type=request.document_type,
        content=document_content,
        status=DocumentStatus.DRAFT,
        word_count=len(document_content),
        version=1
    )

    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)

    return new_document


@router.post("", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """手动创建文档"""
    new_document = Document(
        user_id=current_user.id,
        **document_data.model_dump(),
        word_count=len(document_data.content) if document_data.content else 0
    )

    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)

    return new_document


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    project_id: Optional[int] = Query(None),
    document_type: Optional[DocumentType] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取文档列表"""
    query = select(Document).where(Document.user_id == current_user.id)

    if project_id:
        query = query.where(Document.project_id == project_id)

    if document_type:
        query = query.where(Document.type == document_type)

    if status:
        query = query.where(Document.status == status)

    # 计算总数
    count_result = await db.execute(
        select(func.count(Document.id)).select_from(query.subquery())
    )
    total = count_result.scalar()

    # 获取分页数据
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(Document.updated_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    documents = result.scalars().all()

    return {
        "items": documents,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取文档详情"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新文档"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # 更新字段
    update_data = document_data.model_dump(exclude_unset=True)

    # 如果更新了内容，增加版本号和字数
    if "content" in update_data:
        document.version += 1
        document.word_count = len(update_data["content"])

    for field, value in update_data.items():
        setattr(document, field, value)

    await db.commit()
    await db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    await db.delete(document)
    await db.commit()
    return None
