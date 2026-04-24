import uuid
from sqlalchemy import Column, DateTime, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.models.base import Base

class MCPCredential(Base):
    """
    Stores per-user client credentials for various MCP servers.
    This allows users to provide their own API keys, client IDs, 
    and secrets for services like GitHub, Notion, etc.
    """
    __tablename__ = "mcp_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    server_id = Column(String(50), nullable=False)  # e.g., "github", "notion", "google"
    
    # JSON field to store credentials like:
    # { "api_key": "...", "client_id": "...", "client_secret": "..." }
    credentials = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship back to the user
    user = relationship("User", backref="mcp_credentials")
