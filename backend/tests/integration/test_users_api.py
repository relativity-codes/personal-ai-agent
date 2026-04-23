import pytest

from app.config import settings
from tests.conftest_postgres import postgres_tcp_available

pytestmark = pytest.mark.skipif(
    not postgres_tcp_available(),
    reason="PostgreSQL not reachable (check POSTGRES_* in .env)",
)


@pytest.mark.asyncio
async def test_users_me_get_returns_dev_user(client):
    r = await client.get("/api/v1/users/me")
    assert r.status_code == 200
    data = r.json()
    assert data["clerk_id"] == "dev_bypass"
    assert data["email"] == "dev@localhost"
    assert data["id"] == settings.DEV_USER_INTERNAL_ID
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_users_me_patch_updates_profile(client):
    r = await client.patch(
        "/api/v1/users/me",
        json={"name": "Patched Dev", "timezone": "America/New_York"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Patched Dev"
    assert data["timezone"] == "America/New_York"

    r2 = await client.get("/api/v1/users/me")
    assert r2.status_code == 200
    assert r2.json()["name"] == "Patched Dev"

    await client.patch(
        "/api/v1/users/me",
        json={"name": "Dev User", "timezone": "UTC"},
    )
