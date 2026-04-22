from app.mcp.schema import InvokeRequest, ToolDefinition


def test_invoke_request_defaults():
    r = InvokeRequest(server_id="github", tool="list_open_pull_requests")
    assert r.arguments == {}


def test_tool_definition_schema():
    t = ToolDefinition(name="x", description="d", input_schema={"type": "object"})
    d = t.model_dump()
    assert d["name"] == "x"
    assert d["input_schema"]["type"] == "object"
