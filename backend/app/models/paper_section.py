"""
论文章节模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class PaperSection(Base):
    """论文章节表"""
    __tablename__ = "paper_sections"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    section_number = Column(String(20), nullable=False)  # 章节编号，如 "1", "1.1", "1.1.1"
    title = Column(String(500), nullable=False)
    content = Column(Text)  # Markdown或纯文本内容
    structured_content = Column(JSON)  # 结构化内容（Tiptap JSON格式）
    word_count = Column(Integer, default=0)
    order_index = Column(Integer, nullable=False)  # 排序索引
    parent_id = Column(Integer, ForeignKey("paper_sections.id", ondelete="CASCADE"), nullable=True)  # 父章节ID
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="paper_sections")
    parent = relationship("PaperSection", remote_side=[id], backref="children")
