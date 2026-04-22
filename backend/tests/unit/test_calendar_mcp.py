from types import SimpleNamespace

import pytest

from app.mcp.calendar import CalendarMCPServer


@pytest.mark.asyncio
async def test_list_events_requires_access_token_when_oauth_app_configured():
    settings = SimpleNamespace(
        GOOGLE_CLIENT_ID="test-client",
        GOOGLE_CLIENT_SECRET="test-secret",
        GOOGLE_CALENDAR_ACCESS_TOKEN="",
    )
    server = CalendarMCPServer(settings)  # type: ignore[arg-type]
    out = await server.invoke(
        "list_events",
        {"time_min": "2026-01-01T00:00:00Z", "time_max": "2026-01-02T00:00:00Z"},
    )
    assert out["ok"] is False
    assert out["error"] == "oauth_token_required"
