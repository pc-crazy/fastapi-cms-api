# tests/test_main_extra.py
import pytest

def test_create_account_duplicate_email(client):
    client.post("/accounts", json={"name": "User", "email": "dup@example.com", "password": "pass"})
    res = client.post("/accounts", json={"name": "User2", "email": "dup@example.com", "password": "pass"})
    assert res.status_code == 400
    assert res.json()["detail"] == "Email already registered"

def test_login_invalid_credentials(client):
    res = client.post("/accounts/login", data={"username": "noone@example.com", "password": "wrong", "grant_type": "password"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"

def test_get_nonexistent_post(client):
    from tests.test_blog import create_and_auth_user
    token = create_and_auth_user(client)
    res = client.get("/blog/9999", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"

def test_update_unauthorized_post(client):
    from tests.test_blog import create_and_auth_user
    token1 = create_and_auth_user(client, email="one@example.com")
    res = client.post("/blog", json={"title": "A", "description": "", "content": "", "is_public": True}, headers={"Authorization": f"Bearer {token1}"})
    post_id = res.json()["id"]
    token2 = create_and_auth_user(client, email="two@example.com")
    update_res = client.put(f"/blog/{post_id}", json={"title": "Hack", "description": "", "content": "", "is_public": True}, headers={"Authorization": f"Bearer {token2}"})
    assert update_res.status_code == 403
    assert update_res.json()["detail"] == "Not authorized"

def test_delete_unauthorized_post(client):
    from tests.test_blog import create_and_auth_user
    token1 = create_and_auth_user(client, email="three@example.com")
    res = client.post("/blog", json={"title": "Del", "description": "", "content": "", "is_public": True}, headers={"Authorization": f"Bearer {token1}"})
    post_id = res.json()["id"]
    token2 = create_and_auth_user(client, email="four@example.com")
    del_res = client.delete(f"/blog/{post_id}", headers={"Authorization": f"Bearer {token2}"})
    assert del_res.status_code == 403
    assert del_res.json()["detail"] == "Not authorized"
