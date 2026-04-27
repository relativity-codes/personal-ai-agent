from app.mcp.schema import InvokeRequest, MCPInvokeOAuth, ToolDefinition


def test_invoke_request_defaults():
    r = InvokeRequest(server_id="github", tool="MY_GITHUB_list_prs")
    assert r.arguments == {}
    assert r.oauth is None


def test_invoke_request_with_oauth_overrides():
    r = InvokeRequest(
        server_id="gmail",
        tool="list_threads",
        arguments={"query": "is:unread"},
        oauth=MCPInvokeOAuth(google_refresh_token="user-refresh-token"),
    )
    assert r.oauth is not None
    assert r.oauth.google_refresh_token == "user-refresh-token"


def test_tool_definition_schema():
    t = ToolDefinition(name="x", description="d", input_schema={"type": "object"})
    d = t.model_dump()
    assert d["name"] == "x"
    assert d["input_schema"]["type"] == "object"
