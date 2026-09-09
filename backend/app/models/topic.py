"""
选题模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Topic(Base):
    """选题表"""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    major = Column(String(100), nullable=False)  # 专业
    education_level = Column(String(50), nullable=False)  # 学历层次：adult_education, associate, bachelor, master, phd
    paper_type = Column(String(50), nullable=False)  # 论文类型：text, data, design
    keywords = Column(Text)  # JSON array
    difficulty = Column(String(20))  # easy, medium, hard
    feasibility_score = Column(Float, default=0.0)
    is_used = Column(Boolean, default=False)
    is_selected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="topics")
