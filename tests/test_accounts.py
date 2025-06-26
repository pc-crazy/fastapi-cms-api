# tests/test_accounts.py
import pytest

@pytest.mark.asyncio
async def test_create_account(client):
    response = await client.post("/v1/accounts", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_login_account(client):
    await client.post("/v1/accounts", json={
        "name": "Login User",
        "email": "login@example.com",
        "password": "loginpass"
    })
    response = await client.post("/v1/accounts/login", data={
        "username": "login@example.com",
        "password": "loginpass",
        "grant_type": "password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_get_me(client):
    await client.post("/v1/accounts", json={
        "name": "Me User",
        "email": "me@example.com",
        "password": "mypass"
    })
    login_res = await client.post("/v1/accounts/login", data={
        "username": "me@example.com",
        "password": "mypass",
        "grant_type": "password"
    })
    token = login_res.json()["access_token"]
    me_res = await client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "me@example.com"

@pytest.mark.asyncio
async def test_invalid_token(client):
    res = await client.get("/v1/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert res.status_code == 401

async def register_and_login(client, email="extra@example.com", password="pass123"):
    await client.post("/v1/accounts", json={"name": "Extra", "email": email, "password": password})
    res = await client.post("/v1/accounts/login", data={"username": email, "password": password, "grant_type": "password"})
    return res.json()["access_token"]

@pytest.mark.asyncio
async def test_account_update(client):
    token = await register_and_login(client, "update@example.com")
    res = await client.put("/v1/accounts", json={
        "name": "Updated Name",
        "email": "update@example.com",
        "password": "newpass123"
    }, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Name"

@pytest.mark.asyncio
async def test_account_delete(client):
    token = await register_and_login(client, "delete@example.com")
    res = await client.delete("/v1/accounts", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["message"] == "Account deleted successfully"
