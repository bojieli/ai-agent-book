"""Authorization: Basic credentials must be redacted like Bearer tokens."""
from regex_sanitizer import sanitize


def test_authorization_basic_redacted():
    cred = "dXNlcjpwYXNzd29yZA=="
    text, hits = sanitize(f"Authorization: Basic {cred}")
    assert cred not in text
    assert "[REDACTED_BASIC_AUTH]" in text
    assert any(h["category"] == "basic_auth" for h in hits)


def test_authorization_basic_case_insensitive():
    cred = "YWRtaW46c2VjcmV0"
    text, hits = sanitize(f"authorization: basic {cred}")
    assert cred not in text
    assert "[REDACTED_BASIC_AUTH]" in text


def test_bearer_still_redacted():
    token = "aaaaaaaaaaaaaaaaaaaa"
    text, hits = sanitize(f"Authorization: Bearer {token}")
    assert token not in text
    assert "[REDACTED_BEARER_TOKEN]" in text
    assert any(h["category"] == "bearer_token" for h in hits)
