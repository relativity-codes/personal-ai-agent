import os
import logging
from typing import Optional, Any, Dict, List
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from app.mcp_alt.utils import get_mcp_credentials, save_mcp_credentials
from app.api.schemas import MCPServiceId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-calendar")

server = FastMCP("calendar")

async def get_calendar_service(user_id: Optional[str] = None):


    if not user_id:
        logger.exception("Error refreshing Calender token: No user ID provided")
        return None
    creds_data = await get_mcp_credentials(user_id, MCPServiceId.GOOGLE)
    if not creds_data:
        return None
    token = creds_data.get("access_token")
    refresh_token = creds_data.get("refresh_token")
    client_id = creds_data.get("client_id")
    client_secret = creds_data.get("client_secret")

    if not token and not refresh_token:
        return None

    creds_obj = Credentials(
        token=token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
    )

    # Handle refresh if needed
    if creds_obj.expired and creds_obj.refresh_token:
        try:
            creds_obj.refresh(Request())
            if user_id and creds_data:
                creds_data["access_token"] = creds_obj.token
                await save_mcp_credentials(user_id, MCPServiceId.GOOGLE, creds_data)
        except Exception as e:
            logger.error(f"Failed to refresh calendar token: {e}")

    return build("calendar", "v3", credentials=creds_obj)

@server.tool()
async def list_events(time_min: Optional[str] = None, time_max: Optional[str] = None, max_results: int = 20, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List calendar events."""
    service = await get_calendar_service(user_id)
    if not service:
        return {"ok": False, "error": "not_configured", "message": "Google Calendar not configured."}
    
    now = datetime.utcnow().isoformat() + "Z"
    events_result = service.events().list(
        calendarId="primary",
        timeMin=time_min or now,
        timeMax=time_max,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    return events_result.get("items", [])

@server.tool()
async def detect_overlaps(events: List[Dict[str, Any]], user_id: Optional[str] = None) -> Dict[str, Any]:
    """Find overlapping event intervals (logic stub)."""
    overlaps = []
    for i, a in enumerate(events):
        for j, b in enumerate(events):
            if j <= i: continue
            overlaps.append({"pair": (i, j), "note": "Overlap detection logic is a stub."})
    return {"ok": True, "overlaps": overlaps, "event_count": len(events)}

@server.tool()
async def calendar_fetch_events(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None, 
    date: Optional[str] = None,
    max_results: int = 20, 
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get events from the primary calendar."""
    service = await get_calendar_service(user_id)
    if not service:
        return {"ok": False, "error": "not_configured", "message": "Google Calendar not configured."}
    
    # Handle the case where the planner provides 'date' instead of start/end dates
    if date:
        if not start_date:
            start_date = f"{date}T00:00:00Z"
        if not end_date:
            end_date = f"{date}T23:59:59Z"
            
    if not start_date or not end_date:
        return {
            "ok": False, 
            "error": "missing_parameters", 
            "message": "Either 'start_date' and 'end_date' must be provided, or 'date' must be provided."
        }
    
    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_date,
        timeMax=end_date,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    return {"ok": True, "events": events_result.get("items", [])}

@server.tool()
async def calendar_find_free_slots(date: str, duration_minutes: int, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Find available time slots (mock)."""
    return {"ok": True, "message": "Free slot finding is a mock and not fully implemented."}

@server.tool()
async def calendar_create_event(title: str, start_time: str, end_time: str, attendees: Optional[List[str]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a new event."""
    service = await get_calendar_service(user_id)
    if not service:
        return {"ok": False, "error": "not_configured", "message": "Google Calendar not configured."}
    
    event = {
        "summary": title,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
        "attendees": [{"email": e} for e in (attendees or [])]
    }
    result = service.events().insert(calendarId="primary", body=event).execute()
    return {"ok": True, "event": result}

@server.tool()
async def calendar_get_event(event_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get a single event by ID."""
    service = await get_calendar_service(user_id)
    if not service:
        return {"ok": False, "error": "not_configured", "message": "Google Calendar not configured."}
    
    result = service.events().get(calendarId="primary", eventId=event_id).execute()
    return {"ok": True, "event": result}

@server.tool()
async def calendar_update_event(event_id: str, title: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Update an event."""
    service = await get_calendar_service(user_id)
    if not service:
        return {"ok": False, "error": "not_configured", "message": "Google Calendar not configured."}
    
    event = service.events().get(calendarId="primary", eventId=event_id).execute()
    if title: event["summary"] = title
    if start_time: event["start"]["dateTime"] = start_time
    if end_time: event["end"]["dateTime"] = end_time
    
    result = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
    return {"ok": True, "event": result}

@server.tool()
async def calendar_delete_event(event_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Delete an event."""
    service = await get_calendar_service(user_id)
    if not service:
        return {"ok": False, "error": "not_configured", "message": "Google Calendar not configured."}
    
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    return {"ok": True, "status": "deleted"}

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(main())
