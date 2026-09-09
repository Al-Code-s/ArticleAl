"""
AI配置模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class AiConfig(Base):
    """AI配置表"""
    __tablename__ = "ai_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    config_type = Column(String(50), nullable=False)  # content_generation（内容生成） 或 agent（智能体）
    name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # anthropic, openai, custom
    model_name = Column(String(100), nullable=False)
    api_key = Column(Text, nullable=False)  # 加密存储
    api_base_url = Column(String(255), nullable=True)
    temperature = Column(String(10), default="0.7")
    max_tokens = Column(Integer, default=4096)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="ai_configs")
