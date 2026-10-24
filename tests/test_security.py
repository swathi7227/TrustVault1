
import time

import jwt
import pytest

from backend.app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from backend.app.core.config import settings


def test_password_is_hashed():
    password = "TrustVault-Test-Password-123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)


def test_wrong_password_is_rejected():
    hashed = hash_password("Correct-Password-123!")

    assert not verify_password("Wrong-Password-123!", hashed)


def test_same_password_produces_different_hashes():
    password = "TrustVault-Test-Password-123!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)


def test_access_token_contains_user_and_role():
    token = create_access_token(user_id=123, role="user")
    payload = decode_access_token(token)

    assert payload["sub"] == "123"
    assert payload["role"] == "user"
    assert "exp" in payload
    assert "iat" in payload


def test_invalid_token_is_rejected():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("this-is-not-a-valid-token")


def test_token_signed_with_wrong_secret_is_rejected():
    token = create_access_token(user_id=123, role="user")

    wrong_secret = "not-the-real-secret-for-this-test"
    forged_token = jwt.encode(
        {
            "sub": "123",
            "role": "user",
            "exp": int(time.time()) + 300,
        },
        wrong_secret,
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(forged_token)
