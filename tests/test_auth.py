# tests/test_auth.py
import pytest
import jwt
import os
from datetime import timedelta

from src.auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM


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
    token = create_access_token({"sub": "123"}, expires_delta=timedelta(minutes=1))
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "123"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_invalid_token_signature(client):
    invalid_token = jwt.encode({"sub": "123"}, "wrong-secret", algorithm=ALGORITHM)
    res = await client.get("/v1/me", headers={"Authorization": f"Bearer {invalid_token}"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"


@pytest.mark.asyncio
async def test_token_missing_sub(client):
    token = jwt.encode({}, SECRET_KEY, algorithm=ALGORITHM)
    res = await client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"


@pytest.mark.asyncio
async def test_token_with_nonexistent_user(client):
    token = jwt.encode({"sub": "9999"}, SECRET_KEY, algorithm=ALGORITHM)
    res = await client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Could not validate credentials"

@pytest.mark.asyncio
async def test_valid_token_get_current_user(client):
    email = "covered@example.com"
    password = "testpass"

    # Create user
    res = await client.post("/v1/accounts", json={
        "name": "Tester",
        "email": email,
        "password": password
    })
    assert res.status_code == 200

    # Login
    login = await client.post("/v1/accounts/login", data={
        "username": email,
        "password": password,
        "grant_type": "password"
    })
    assert login.status_code == 200
    token = login.json().get("access_token")
    assert token

    # Access a route that uses get_current_user()
    res = await client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == email