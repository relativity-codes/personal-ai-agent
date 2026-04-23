import uuid

from sqlalchemy import Boolean, Column, DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255))
    avatar_url = Column(String(500))
    default_github_repo = Column(String(255))
    default_notion_db = Column(String(255))
    timezone = Column(String(50), default="UTC")
    working_hours_start = Column(String(5), default="09:00")
    working_hours_end = Column(String(5), default="17:00")
    mcp_tokens = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    plans = relationship("ExecutionPlan", back_populates="user", cascade="all, delete-orphan")
