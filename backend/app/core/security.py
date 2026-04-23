from __future__ import annotations

import logging
from typing import Any

import jwt
from jwt import PyJWKClient

from app.config import settings

logger = logging.getLogger(__name__)

_jwks_client: PyJWKClient | None = None


def _jwks() -> PyJWKClient | None:
    global _jwks_client
    issuer = (settings.CLERK_ISSUER or "").strip().rstrip("/")
    if not issuer:
        return None
    if _jwks_client is None:
        url = f"{issuer}/.well-known/jwks.json"
        _jwks_client = PyJWKClient(url)
    return _jwks_client


def decode_clerk_session_token(token: str) -> dict[str, Any]:
    """
    Verify a Clerk session JWT (RS256/ES256 via JWKS).
    Set ``CLERK_ISSUER`` to your Frontend API URL, e.g. ``https://xxx.clerk.accounts.dev``.
    """
    issuer = (settings.CLERK_ISSUER or "").strip().rstrip("/")
    if not issuer:
        raise ValueError("CLERK_ISSUER is not configured")
    client = _jwks()
    if client is None:
        raise ValueError("JWKS client not available")
    signing_key = client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        issuer=issuer,
        options={"verify_aud": False},
    )


def claims_to_profile(claims: dict[str, Any]) -> dict[str, Any]:
    """Normalize Clerk JWT claims for app use."""
    sub = str(claims.get("sub") or "")
    email = ""
    if claims.get("email"):
        email = str(claims["email"])
    elif isinstance(claims.get("email_addresses"), list) and claims["email_addresses"]:
        primary_id = claims.get("primary_email_address_id")
        for entry in claims["email_addresses"]:
            if not isinstance(entry, dict):
                continue
            if primary_id and entry.get("id") == primary_id:
                email = str(entry.get("email_address") or "")
                break
        if not email:
            first = claims["email_addresses"][0]
            if isinstance(first, dict) and first.get("email_address"):
                email = str(first["email_address"])
    name = claims.get("name")
    if not name and isinstance(claims.get("given_name"), str):
        name = claims.get("given_name")
    picture = claims.get("picture") or claims.get("image_url")
    return {
        "clerk_sub": sub,
        "email": email,
        "name": str(name) if name else None,
        "avatar_url": str(picture) if picture else None,
    }
