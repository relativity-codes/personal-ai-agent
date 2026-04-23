from sqlalchemy import Column, String, DateTime, JSON, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False)
    input_text = Column(String(5000))
    intent_type = Column(String(50))
    plan_id = Column(UUID(as_uuid=True))
    success = Column(Boolean, default=True)
    error_message = Column(String(500))
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    event_metadata = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
