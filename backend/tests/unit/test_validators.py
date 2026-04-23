import uuid

import pytest
from fastapi import HTTPException

from app.utils.validators import parse_bearer_token, parse_uuid


def test_parse_bearer_token_none_and_empty():
    assert parse_bearer_token(None) is None
    assert parse_bearer_token("") is None
    assert parse_bearer_token("Basic x") is None


def test_parse_bearer_token_valid():
    assert parse_bearer_token("Bearer abc.def.ghi") == "abc.def.ghi"
    assert parse_bearer_token("bearer token_only") == "token_only"


def test_parse_uuid_valid():
    u = uuid.uuid4()
    assert parse_uuid(str(u)) == u


def test_parse_uuid_invalid():
    with pytest.raises(HTTPException) as exc:
        parse_uuid("not-a-uuid", field="plan_id")
    assert exc.value.status_code == 400
    assert "plan_id" in exc.value.detail
