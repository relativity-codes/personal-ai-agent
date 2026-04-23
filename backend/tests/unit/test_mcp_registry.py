import pytest

from app.mcp.registry import MCPRegistryService


@pytest.mark.asyncio
async def test_registry_registers_four_integrations():
    reg = MCPRegistryService()
    await reg.initialize()
    servers = reg.list_servers()
    assert len(servers) == 4
    ids = {s["id"] for s in servers}
    assert ids == {"github", "notion", "calendar", "gmail"}
    summary = reg.summary()
    assert summary["total"] == 4
    assert 0 <= summary["configured"] <= 4


@pytest.mark.asyncio
async def test_registry_list_all_tools_non_empty():
    reg = MCPRegistryService()
    await reg.initialize()
    integrations = await reg.list_all_tools()
    assert len(integrations) == 4
    for block in integrations:
        assert block["server_id"]
        assert len(block["tools"]) >= 1
