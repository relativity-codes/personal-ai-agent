import pytest

from app.config import settings


@pytest.mark.asyncio
async def test_users_me_401_when_bypass_off_and_no_token(client, monkeypatch):
    monkeypatch.setattr(settings, "DEV_AUTH_BYPASS", False)
    r = await client.get("/api/v1/users/me")
    assert r.status_code == 401
    assert "Missing bearer token" in r.json()["detail"]


@pytest.mark.asyncio
async def test_users_me_503_when_bypass_off_and_issuer_not_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "DEV_AUTH_BYPASS", False)
    monkeypatch.setattr(settings, "CLERK_ISSUER", "")
    r = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert r.status_code == 503
    assert "CLERK_ISSUER" in r.json()["detail"]
