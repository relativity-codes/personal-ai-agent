from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class ExecutionPlan(Base):
    __tablename__ = "execution_plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    intent_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    tasks = Column(JSON, nullable=False)
    task_status = Column(JSON, default=dict)
    task_results = Column(JSON, default=dict)
    task_errors = Column(JSON, default=dict)
    execution_order = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    user = relationship("User", back_populates="plans")
