import base64

import pytest

from app.config import settings
from app.db.repositories.user_repository import UserRepository
from app.db.session import async_session_factory
from tests.conftest_postgres import postgres_tcp_available


def _valid_whsec_secret() -> str:
    return "whsec_" + base64.b64encode(b"k" * 24).decode("ascii")


@pytest.mark.asyncio
async def test_clerk_webhook_503_when_secret_not_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "CLERK_WEBHOOK_SECRET", "")
    r = await client.post("/api/v1/webhooks/clerk", content=b"{}")
    assert r.status_code == 503


@pytest.mark.asyncio
async def test_clerk_webhook_400_on_invalid_signature(client, monkeypatch):
    monkeypatch.setattr(settings, "CLERK_WEBHOOK_SECRET", _valid_whsec_secret())
    r = await client.post(
        "/api/v1/webhooks/clerk",
        content=b'{"type":"user.created"}',
        headers={
            "svix-id": "msg_1",
            "svix-timestamp": "1",
            "svix-signature": "v1,invalid",
        },
    )
    assert r.status_code == 400


@pytest.mark.asyncio
@pytest.mark.skipif(
    not postgres_tcp_available(),
    reason="PostgreSQL not reachable (check POSTGRES_* in .env)",
)
async def test_clerk_webhook_200_processes_signed_payload(client, monkeypatch):
    """Bypass Svix crypto: stub verifier, assert user sync runs."""

    def fake_verify(body: bytes, headers: dict[str, str]) -> dict:
        return {
            "type": "user.created",
            "data": {
                "id": "user_test_webhook_upsert",
                "primary_email_address_id": "ea_1",
                "email_addresses": [
                    {"id": "ea_1", "email_address": "webhook.user@example.com"},
                ],
                "first_name": "Webhook",
                "last_name": "Test",
            },
        }

    monkeypatch.setattr(settings, "CLERK_WEBHOOK_SECRET", _valid_whsec_secret())
    monkeypatch.setattr("app.api.v1.webhooks.verify_clerk_signature", fake_verify)

    r = await client.post("/api/v1/webhooks/clerk", content=b"{}")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    async with async_session_factory() as session:
        row = await UserRepository.get_by_clerk_id(session, "user_test_webhook_upsert")
        assert row is not None
        assert row.email == "webhook.user@example.com"
        assert row.name == "Webhook Test"
