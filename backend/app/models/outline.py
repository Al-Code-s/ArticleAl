"""
大纲模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Outline(Base):
    """大纲表"""
    __tablename__ = "outlines"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    title = Column(String(500), nullable=False)
    word_count = Column(Integer, nullable=False)
    structure = Column(JSON, nullable=False)  # 大纲结构
    # structure格式示例:
    # [
    #   {"level": 1, "title": "摘要", "content": ""},
    #   {"level": 1, "title": "引言", "content": ""},
    #   {"level": 2, "title": "研究背景", "content": ""},
    # ]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="outline")
