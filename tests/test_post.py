# tests/test_main_extra.py
import pytest
from tests.test_blog import create_and_auth_user
from fastapi.testclient import TestClient
from src.main import app

@pytest.mark.asyncio
async def test_create_account_duplicate_email(client):
    await client.post("/v1/accounts", json={"name": "User", "email": "dup@example.com", "password": "pass"})
    res = await client.post("/v1/accounts", json={"name": "User2", "email": "dup@example.com", "password": "pass"})
    assert res.status_code == 400
    assert res.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    res = await client.post("/v1/accounts/login", data={"username": "noone@example.com", "password": "wrong", "grant_type": "password"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"

@pytest.mark.asyncio
async def test_get_nonexistent_post(client):
    token = await create_and_auth_user(client)
    res = await client.get("/v1/blog/9999", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"

@pytest.mark.asyncio
async def test_update_unauthorized_post(client):
    token1 = await create_and_auth_user(client, email="one@example.com")
    res = await client.post("/v1/blog", json={"title": "A", "description": "", "content": "", "is_public": True}, headers={"Authorization": f"Bearer {token1}"})
    post_id = res.json()["id"]
    token2 = await create_and_auth_user(client, email="two@example.com")
    update_res = await client.put(f"/v1/blog/{post_id}", json={"title": "Hack", "description": "", "content": "", "is_public": True}, headers={"Authorization": f"Bearer {token2}"})
    assert update_res.status_code == 403
    assert update_res.json()["detail"] == "Not authorized"

@pytest.mark.asyncio
async def test_delete_unauthorized_post(client):
    token1 = await create_and_auth_user(client, email="three@example.com")
    res = await client.post("/v1/blog", json={"title": "Del", "description": "", "content": "", "is_public": True}, headers={"Authorization": f"Bearer {token1}"})
    post_id = res.json()["id"]
    token2 = await create_and_auth_user(client, email="four@example.com")
    del_res = await client.delete(f"/v1/blog/{post_id}", headers={"Authorization": f"Bearer {token2}"})
    assert del_res.status_code == 403
    assert del_res.json()["detail"] == "Not authorized"

def test_startup_trigger():
    with TestClient(app) as client:
        res = client.get("/v1/blog")
        assert res.status_code in [200, 401, 403]

