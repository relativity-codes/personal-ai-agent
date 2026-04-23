import httpx

from app.mcp.notion import _notion_upstream_error


def test_notion_upstream_error_adds_hint_for_create_page_404() -> None:
    r = httpx.Response(
        404,
        json={
            "object": "error",
            "code": "object_not_found",
            "message": "Could not find page with ID: x. Make sure ... shared with your integration.",
        },
    )
    out = _notion_upstream_error(r, tool_name="create_page", parent_type="page_id")
    assert out["ok"] is False
    assert out["status_code"] == 404
    assert "hint" in out
    assert "Connections" in out["hint"]
    assert "database_id" in out["hint"]


def test_notion_upstream_error_page_not_database_400() -> None:
    r = httpx.Response(
        400,
        json={
            "object": "error",
            "status": 400,
            "code": "validation_error",
            "message": "Provided database_id 34a0e570-56a6-80a8-b010-e4d260bc1534 is a page, not a database.",
        },
    )
    out = _notion_upstream_error(r, tool_name="create_page", parent_type="database_id")
    assert out["status_code"] == 400
    assert "hint" in out
    assert "page_id" in out["hint"]
