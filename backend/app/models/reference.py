"""
参考文献模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Reference(Base):
    """参考文献表"""
    __tablename__ = "references"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    authors = Column(Text, nullable=False)  # JSON array
    journal = Column(String(200))
    year = Column(Integer)
    volume = Column(String(50))
    issue = Column(String(50))
    pages = Column(String(50))
    doi = Column(String(100))
    url = Column(Text)
    abstract = Column(Text)
    keywords = Column(Text)  # JSON array

    # 知网特有字段
    cnki_url = Column(Text)
    citation_count = Column(Integer, default=0)

    # 引用格式
    citation_format = Column(Text)  # GB/T 7714格式的引用

    # 是否被选中使用
    is_selected = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="references")
