# test_auth.py
import os
from datetime import timedelta

import jwt

from src.auth import create_access_token, get_password_hash, verify_password

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"


def test_get_password_hash_and_verify():
    raw_password = "test123"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed)
    assert not verify_password("wrongpass", hashed)


def test_create_access_token_structure():
    token = create_access_token({"sub": "1"})
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "1"
    assert "exp" in decoded


def test_create_access_token_expiry():
    token = create_access_token(
        {"sub": "123"}, expires_delta=timedelta(minutes=1)
    )
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "123"
    assert "exp" in decoded


def test_invalid_token_signature(client):
    # Token signed with wrong secret key
    invalid_token = jwt.encode(
        {"sub": "123"}, "wrong-secret", algorithm=ALGORITHM
    )
    res = client.get(
        "/v1/me", headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"


def test_token_missing_sub(client):
    # Token without 'sub' field
    token = jwt.encode({}, SECRET_KEY, algorithm=ALGORITHM)
    res = client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"


def test_token_with_nonexistent_user(client):
    # Token with non-existent user ID
    token = jwt.encode({"sub": "9999"}, SECRET_KEY, algorithm=ALGORITHM)
    res = client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"
