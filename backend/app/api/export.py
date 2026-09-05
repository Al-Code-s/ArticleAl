"""
导出 API 路由
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Literal

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.services.export_service import export_service

router = APIRouter()


class ExportRequest(BaseModel):
    """导出请求"""
    document_id: int
    format: Literal["word", "pdf"] = "word"


@router.post("/document/{document_id}")
async def export_document(
    document_id: int,
    format: Literal["word", "pdf"] = "word",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    导出文档为 Word 或 PDF

    Args:
        document_id: 文档ID
        format: 导出格式 (word 或 pdf)
    """
    # 获取文档
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

    # 准备元数据
    metadata = {
        "author": current_user.username,
        "date": document.created_at.strftime("%Y-%m-%d"),
    }

    # 导出文档
    try:
        if format == "word":
            filepath = await export_service.export_to_word(
                title=document.title,
                content=document.content,
                metadata=metadata
            )
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = filepath.split('\\')[-1] if '\\' in filepath else filepath.split('/')[-1]

        else:  # pdf
            filepath = await export_service.export_to_pdf(
                title=document.title,
                content=document.content,
                metadata=metadata
            )
            media_type = "application/pdf"
            filename = filepath.split('\\')[-1] if '\\' in filepath else filepath.split('/')[-1]

        # 返回文件
        return FileResponse(
            path=filepath,
            media_type=media_type,
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.post("/custom")
async def export_custom(
    title: str,
    content: str,
    format: Literal["word", "pdf"] = "word",
    current_user: User = Depends(get_current_user)
):
    """
    导出自定义内容

    Args:
        title: 文档标题
        content: 文档内容（Markdown）
        format: 导出格式
    """
    metadata = {
        "author": current_user.username,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    try:
        if format == "word":
            filepath = await export_service.export_to_word(
                title=title,
                content=content,
                metadata=metadata
            )
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = filepath.split('\\')[-1] if '\\' in filepath else filepath.split('/')[-1]

        else:  # pdf
            filepath = await export_service.export_to_pdf(
                title=title,
                content=content,
                metadata=metadata
            )
            media_type = "application/pdf"
            filename = filepath.split('\\')[-1] if '\\' in filepath else filepath.split('/')[-1]

        return FileResponse(
            path=filepath,
            media_type=media_type,
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )
