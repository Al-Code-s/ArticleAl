"""
大纲模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Outline(Base):
    """大纲表"""
    __tablename__ = "outlines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    title = Column(String(500), nullable=False)
    content = Column(JSON, nullable=False)  # 大纲内容 (从 structure 改为 content，与 schema 匹配)
    # 旧版本数据库仍保留非空 structure 字段，写入同一份结构保持兼容
    structure = Column(JSON, nullable=False, default=dict)
    # 兼容数据库中用于统计大纲字数的非空字段
    word_count = Column(Integer, nullable=False, default=0)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="outlines")
    project = relationship("Project", back_populates="outline")
