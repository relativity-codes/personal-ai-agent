from app.core.security import claims_to_profile


def test_claims_to_profile_email_field():
    claims = {"sub": "user_2abc", "email": "hello@example.com", "name": "Hello"}
    p = claims_to_profile(claims)
    assert p["clerk_sub"] == "user_2abc"
    assert p["email"] == "hello@example.com"
    assert p["name"] == "Hello"


def test_claims_to_profile_email_addresses_primary():
    claims = {
        "sub": "user_xyz",
        "primary_email_address_id": "ea_1",
        "email_addresses": [
            {"id": "ea_other", "email_address": "other@x.com"},
            {"id": "ea_1", "email_address": "primary@x.com"},
        ],
    }
    p = claims_to_profile(claims)
    assert p["clerk_sub"] == "user_xyz"
    assert p["email"] == "primary@x.com"


def test_claims_to_profile_given_name_and_picture():
    claims = {"sub": "u1", "given_name": "Pat", "picture": "https://cdn.example/p.png"}
    p = claims_to_profile(claims)
    assert p["name"] == "Pat"
    assert p["avatar_url"] == "https://cdn.example/p.png"
