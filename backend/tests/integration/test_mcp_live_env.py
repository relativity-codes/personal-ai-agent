from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.config import settings
from app.mcp.calendar import CalendarMCPServer
from app.mcp.registry import MCPRegistryService


def _skip_if_no_github_token() -> None:
    if not settings.MY_GITHUB_TOKEN.strip():
        pytest.skip("Set MY_GITHUB_TOKEN in backend/.env for live GitHub tests")


def _skip_if_no_notion_db() -> None:
    if not settings.NOTION_TOKEN.strip():
        pytest.skip("Set NOTION_TOKEN in backend/.env for live Notion tests")
    if not settings.NOTION_TEST_DATABASE_ID.strip():
        pytest.skip("Set NOTION_TEST_DATABASE_ID in backend/.env (database shared with your integration)")


def _skip_if_no_calendar_api_auth() -> None:
    pytest.skip(
        "Calendar live tests now require user-scoped OAuth credentials stored in DB; "
        "seed creds via /api/v1/mcp/oauth/google/callback then run manually."
    )


def _skip_if_no_gmail_api_auth() -> None:
    pytest.skip(
        "Gmail live tests now require user-scoped OAuth credentials stored in DB; "
        "seed creds via /api/v1/mcp/oauth/google/callback then run manually."
    )


def _calendar_oauth_message_scenario() -> bool:
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_github_list_pull_requests_via_http(client):
    _skip_if_no_github_token()
    r = await client.post(
        "/api/v1/mcp/invoke",
        json={
            "server_id": "github",
            "tool": "github_list_prs",
            "arguments": {
                "owner": settings.MY_GITHUB_TEST_OWNER,
                "repo": settings.MY_GITHUB_TEST_REPO,
                "state": "open",
            },
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert isinstance(body["result"].get("data"), list)


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_github_list_commits_via_registry():
    _skip_if_no_github_token()
    reg = MCPRegistryService()
    await reg.initialize()
    gh = reg.get("github")
    assert gh is not None
    out = await gh.invoke(
        "github_list_commits",
        {
            "owner": settings.MY_GITHUB_TEST_OWNER,
            "repo": settings.MY_GITHUB_TEST_REPO,
            "branch": "master",
        },
    )
    assert out["ok"] is True
    assert isinstance(out.get("data"), list)


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_notion_query_database_via_http(client):
    _skip_if_no_notion_db()
    r = await client.post(
        "/api/v1/mcp/invoke",
        json={
            "server_id": "notion",
            "tool": "query_database",
            "arguments": {
                "database_id": settings.NOTION_TEST_DATABASE_ID.strip(),
                "page_size": 3,
            },
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "results" in body["result"]["data"]


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_calendar_list_events_real_api():
    _skip_if_no_calendar_api_auth()
    srv = CalendarMCPServer(settings)
    now = datetime.now(timezone.utc)
    time_min = now.isoformat().replace("+00:00", "Z")
    time_max = (now + timedelta(days=7)).isoformat().replace("+00:00", "Z")
    out = await srv.invoke(
        "list_events",
        {"time_min": time_min, "time_max": time_max, "max_results": 10},
    )
    assert out["ok"] is True
    assert isinstance(out.get("events"), list)


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_calendar_list_events_oauth_token_required_with_real_env():
    if not _calendar_oauth_message_scenario():
        pytest.skip(
            "Requires GOOGLE_CLIENT_ID+GOOGLE_CLIENT_SECRET set"
        )
    srv = CalendarMCPServer(settings)
    now = datetime.now(timezone.utc)
    time_min = now.isoformat().replace("+00:00", "Z")
    time_max = (now + timedelta(days=1)).isoformat().replace("+00:00", "Z")
    out = await srv.invoke(
        "list_events",
        {"time_min": time_min, "time_max": time_max},
    )
    assert out["ok"] is False
    assert out.get("error") in ("oauth_token_required", "not_configured")


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_gmail_list_threads_via_http(client):
    _skip_if_no_gmail_api_auth()
    r = await client.post(
        "/api/v1/mcp/invoke",
        json={
            "server_id": "gmail",
            "tool": "list_threads",
            "arguments": {"query": "is:unread", "max_results": 5},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    data = body["result"]["data"]
    assert isinstance(data, dict)
    assert "threads" in data or "resultSizeEstimate" in data
