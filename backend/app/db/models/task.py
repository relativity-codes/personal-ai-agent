from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.models.base import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("execution_plans.id"), nullable=False)
    step = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    mcp_server = Column(String, nullable=False)
    tool = Column(String, nullable=False)
    parameters = Column(JSON, nullable=False)
    depends_on = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    plan = relationship("ExecutionPlan", back_populates="tasks")
