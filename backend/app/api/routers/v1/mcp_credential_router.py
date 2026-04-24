from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import CurrentUser, get_current_user, parse_uuid
from app.db.database import get_db
from app.db.repositories.mcp_credential_repository import MCPCredentialRepository
from app.api.schemas import (
    MCPCredentialRead, 
    MCPCredentialCreate, 
    MCPCredentialUpdate,
    GitHubCredentials,
    NotionCredentials,
    GoogleCredentials,
    MCPServiceId
)

router = APIRouter()

def validate_credentials_data(server_id: str, credentials: dict):
    try:
        if server_id == MCPServiceId.GITHUB:
            GitHubCredentials(**credentials)
        elif server_id == MCPServiceId.NOTION:
            NotionCredentials(**credentials)
        elif server_id in [MCPServiceId.GOOGLE, MCPServiceId.CALENDAR, MCPServiceId.GMAIL]:
            GoogleCredentials(**credentials)
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid credentials format for {server_id}: {str(e)}"
        )

@router.get("/", response_model=List[MCPCredentialRead])
async def list_credentials(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """List all MCP credentials for the current user."""
    uid = parse_uuid(user["user_id"], "user_id")
    return await MCPCredentialRepository.get_by_user(db, uid)

@router.post("/", response_model=MCPCredentialRead)
async def create_credential(
    body: MCPCredentialCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Create a new MCP credential for the current user."""
    uid = parse_uuid(user["user_id"], "user_id")
    
    # Check if credential for this server already exists
    existing = await MCPCredentialRepository.get_by_user_and_server(db, uid, body.server_id)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Credential for server '{body.server_id}' already exists. Use PATCH to update."
        )
    
    # credentials is now a typed model, convert back to dict for storage
    creds_dict = body.credentials.model_dump() if hasattr(body.credentials, "model_dump") else body.credentials

    credential = await MCPCredentialRepository.create(
        db, uid, body.server_id, creds_dict
    )
    await db.commit()
    await db.refresh(credential)
    return credential

@router.get("/{server_id}", response_model=MCPCredentialRead)
async def get_credential(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Get credential for a specific MCP server."""
    uid = parse_uuid(user["user_id"], "user_id")
    credential = await MCPCredentialRepository.get_by_user_and_server(db, uid, server_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    return credential

@router.patch("/{credential_id}", response_model=MCPCredentialRead)
async def update_credential(
    credential_id: UUID,
    body: MCPCredentialUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Update an existing MCP credential."""
    uid = parse_uuid(user["user_id"], "user_id")
    db_credential = await MCPCredentialRepository.get_by_id(db, credential_id)
    
    if not db_credential or db_credential.user_id != uid:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    
    if body.credentials is not None:
        # Validate credentials format
        validate_credentials_data(db_credential.server_id, body.credentials)
        
        updated = await MCPCredentialRepository.update(db, credential_id, body.credentials)
        await db.commit()
        await db.refresh(updated)
        return updated
        
    return db_credential

@router.delete("/{credential_id}")
async def delete_credential(
    credential_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Delete an MCP credential."""
    uid = parse_uuid(user["user_id"], "user_id")
    db_credential = await MCPCredentialRepository.get_by_id(db, credential_id)
    
    if not db_credential or db_credential.user_id != uid:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    await MCPCredentialRepository.delete(db, credential_id)
    await db.commit()
    return {"ok": True}
