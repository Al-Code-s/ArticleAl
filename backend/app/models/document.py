"""
文档模型（任务书、开题报告、文献综述、论文正文）
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class DocumentType(str, enum.Enum):
    """文档类型"""
    ASSIGNMENT = "assignment"  # 任务书
    PROPOSAL = "proposal"  # 开题报告
    LITERATURE_REVIEW = "literature_review"  # 文献综述
    THESIS = "thesis"  # 论文正文


class DocumentStatus(str, enum.Enum):
    """文档状态"""
    DRAFT = "draft"  # 草稿
    COMPLETED = "completed"  # 已完成
    REVIEWED = "reviewed"  # 已审阅


class Document(Base):
    """文档表"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    # String columns keep compatibility with databases created before the enum migration.
    type = Column(String(50), nullable=False)
    status = Column(String(50), default=DocumentStatus.DRAFT.value)
    title = Column(String(500), nullable=False)
    content = Column(Text)  # Markdown或纯文本内容
    word_count = Column(Integer, default=0)  # 字数统计
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="documents")
    project = relationship("Project", back_populates="documents")
