"""Per-user overrides for the bundled writing skills."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from app.core.database import Base


class SkillOverride(Base):
    __tablename__ = "skill_overrides"
    __table_args__ = (UniqueConstraint("user_id", "skill_key"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_key = Column(String(50), nullable=False)
    instructions = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
