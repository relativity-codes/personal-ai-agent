import pytest

from app.config import settings


@pytest.mark.asyncio
async def test_mcp_servers_lists_integrations(client):
    r = await client.get("/api/v1/mcp/servers")
    assert r.status_code == 200
    data = r.json()
    assert "servers" in data
    ids = {s["id"] for s in data["servers"]}
    assert ids == {"github", "notion", "calendar", "gmail"}
    for s in data["servers"]:
        assert "configured" in s
        assert "description" in s


@pytest.mark.asyncio
async def test_mcp_tools_lists_tool_catalog(client):
    r = await client.get("/api/v1/mcp/tools")
    assert r.status_code == 200
    data = r.json()
    assert "integrations" in data
    by_id = {b["server_id"]: b for b in data["integrations"]}
    assert "MY_GITHUB_list_prs" in {t["name"] for t in by_id["github"]["tools"]}
    assert "query_database" in {t["name"] for t in by_id["notion"]["tools"]}


@pytest.mark.asyncio
async def test_mcp_invoke_unknown_server(client):
    r = await client.post(
        "/api/v1/mcp/invoke",
        json={"server_id": "unknown", "tool": "x", "arguments": {}},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_mcp_invoke_unknown_tool(client):
    r = await client.post(
        "/api/v1/mcp/invoke",
        json={"server_id": "github", "tool": "nonexistent", "arguments": {}},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_mcp_invoke_calendar_overlap_helper(client):
    r = await client.post(
        "/api/v1/mcp/invoke",
        json={
            "server_id": "calendar",
            "tool": "detect_overlaps",
            "arguments": {"events": [{"id": 1}, {"id": 2}]},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["result"]["event_count"] == 2


@pytest.mark.asyncio
async def test_health_includes_mcp_summary(client):
    r = await client.get("/health")
    assert r.status_code == 200
    mcp = r.json()["services"]["mcp"]
    assert mcp["total"] == 4
    assert "configured" in mcp


@pytest.mark.asyncio
async def test_mcp_oauth_status(client):
    r = await client.get("/api/v1/mcp/oauth/status")
    assert r.status_code == 200
    body = r.json()
    assert body["google"]["invoke_oauth_fields"]
    assert "MY_GITHUB_token" in body["github"]["invoke_oauth_fields"]


@pytest.mark.asyncio
async def test_mcp_google_authorize_url(client):
    r = await client.get(
        "/api/v1/mcp/oauth/google/authorize-url",
        params={"redirect_uri": "http://localhost:3000/oauth/callback"},
    )
    if not settings.GOOGLE_CLIENT_ID:
        assert r.status_code == 503
    else:
        assert r.status_code == 200
        url = r.json()["url"]
        assert "accounts.google.com" in url
        assert "client_id=" in url
        assert "redirect_uri=" in url
