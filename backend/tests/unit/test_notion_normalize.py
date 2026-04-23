import pytest

from app.mcp.notion import normalize_notion_resource_id

HEX32 = "34a0e57056a680a8b010e4d260bc1534"
UUID_CANON = "34a0e570-56a6-80a8-b010-e4d260bc1534"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (HEX32, UUID_CANON),
        (UUID_CANON, UUID_CANON),
        (UUID_CANON.upper(), UUID_CANON),
        (f"Andela-capstone-{HEX32}", UUID_CANON),
        (f"https://www.notion.so/Andela-capstone-{HEX32}", UUID_CANON),
        (f"https://www.notion.so/ws/Andela-capstone-{HEX32}?v=1", UUID_CANON),
        (f'"{HEX32}"', UUID_CANON),
        (f'""{HEX32}""', UUID_CANON),
    ],
)
def test_normalize_notion_resource_id_ok(raw: str, expected: str) -> None:
    assert normalize_notion_resource_id(raw) == expected


def test_normalize_notion_resource_id_invalid() -> None:
    with pytest.raises(ValueError):
        normalize_notion_resource_id("not-a-notion-id")
