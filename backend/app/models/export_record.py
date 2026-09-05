"""
导出记录模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ExportFormat(str, enum.Enum):
    """导出格式"""
    DOCX = "docx"
    PDF = "pdf"


class ExportStatus(str, enum.Enum):
    """导出状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportRecord(Base):
    """导出记录表"""
    __tablename__ = "export_records"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    export_type = Column(String(50), nullable=False)  # task_book, proposal, literature_review, paper
    format = Column(SQLEnum(ExportFormat), nullable=False)
    status = Column(SQLEnum(ExportStatus), default=ExportStatus.PENDING)
    file_path = Column(String(500))
    file_size = Column(Integer)
    error_message = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # 关系（如果需要可以添加）
    # project = relationship("Project", backref="export_records")
