from datetime import datetime, timedelta, timezone

from jose import jwt

from auth_service.infrastructure.security.jwt_service import JWTService


def test_issue_and_decode_token_with_one_hour_lifetime():
    service = JWTService("unit-test-secret-key-that-is-at-least-32-characters")

    issued = service.issue_token(42)
    payload = jwt.get_unverified_claims(issued.encoded_token)

    assert service.decode_token(issued.encoded_token) == issued.claims
    assert payload["sub"] == "42"
    assert payload["exp"] - payload["iat"] == 3600


def test_decode_token_rejects_expired_token():
    service = JWTService("unit-test-secret-key-that-is-at-least-32-characters")
    expired_token = jwt.encode(
        {
            "sub": "42",
            "jti": "expired-token",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        service.secret_key,
        algorithm=service.algorithm,
    )

    assert service.decode_token(expired_token) is None


def test_decode_token_rejects_wrong_signature_and_malformed_input():
    service = JWTService("unit-test-secret-key-that-is-at-least-32-characters")
    other_service = JWTService("another-test-secret-key-that-is-32-characters")
    token = other_service.issue_token(1).encoded_token

    assert service.decode_token(token) is None
    assert service.decode_token("not-a-jwt") is None