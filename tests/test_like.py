# tests/test_like.py
import pytest
import asyncio
from sqlalchemy import delete
from src.models import Post
from src.database import get_db

@pytest.mark.asyncio
async def create_user_and_blog(client, email="liker@example.com", password="likepass", is_public=True):
    await client.post("/v1/accounts", json={
        "name": "Liker",
        "email": email,
        "password": password
    })
    login = await client.post("/v1/accounts/login", data={
        "username": email,
        "password": password,
        "grant_type": "password"
    })
    assert login.status_code == 200, f"Login failed: {login.json()}"
    token = login.json().get("access_token")
    assert token, "access_token not found in login response"

    post = await client.post("/v1/blog", json={
        "title": "Like Test",
        "description": "Test desc",
        "content": "Test content",
        "is_public": is_public
    }, headers={"Authorization": f"Bearer {token}"})
    assert post.status_code == 200, f"Post creation failed: {post.json()}"

    return token, post.json()["id"]

@pytest.mark.asyncio
async def test_like_post(client):
    token, blog_id = await create_user_and_blog(client)
    like_res = await client.post(f"/v1/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert like_res.status_code == 200
    assert like_res.json()["message"] == "Post liked"

@pytest.mark.asyncio
async def test_like_post_twice(client):
    token, blog_id = await create_user_and_blog(client, email="liketwice@example.com")
    await client.post(f"/v1/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    like_again = await client.post(f"/v1/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert like_again.status_code == 400
    assert like_again.json()["detail"] == "You have already liked this post."

@pytest.mark.asyncio
async def test_unlike_post(client):
    token, blog_id = await create_user_and_blog(client, email="unliker@example.com")
    await client.post(f"/v1/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    unlike_res = await client.delete(f"/v1/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert unlike_res.status_code == 200
    assert unlike_res.json()["message"] == "Post unliked"

@pytest.mark.asyncio
async def test_unlike_post_not_liked(client):
    token, blog_id = await create_user_and_blog(client, email="nolike@example.com")
    unlike_res = await client.delete(f"/v1/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert unlike_res.status_code == 400
    assert unlike_res.json()["detail"] == "You have not liked this post"

@pytest.mark.asyncio
async def test_like_invalid_post(client):
    token, _ = await create_user_and_blog(client, email="invalidlike@example.com")
    res = await client.post("/v1/like/9999", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"

@pytest.mark.asyncio
async def test_unlike_invalid_post(client):
    token, _ = await create_user_and_blog(client, email="invalidunlike@example.com")
    res = await client.delete("/v1/like/9999", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"

@pytest.mark.asyncio
async def test_like_private_post_not_owner(client):
    # Clean blog table if needed
    async for db in get_db():
        await db.execute(delete(Post))
        await db.commit()
    await asyncio.sleep(5)
    # User 1 creates private post
    owner_email = "blogowner@example.com"
    owner_pass = "ownerpass"
    create_res1 = await client.post("/v1/accounts", json={"name": "Owner", "email": owner_email, "password": owner_pass})
    assert create_res1.status_code == 200, f"User1 creation failed: {create_res1.json()}"
    await asyncio.sleep(5)
    login1 = await client.post("/v1/accounts/login", data={"username": owner_email, "password": owner_pass, "grant_type": "password"})
    assert login1.status_code == 200, f"Login1 failed: {login1.json()}"
    token1 = login1.json().get("access_token")
    assert token1

    post = await client.post("/v1/blog", json={
        "title": "Private Post",
        "description": "Private desc",
        "content": "Hidden content",
        "is_public": False
    }, headers={"Authorization": f"Bearer {token1}"})
    assert post.status_code == 200, f"Post creation failed: {post.json()}"
    blog_id = post.json()["id"]

    # User 2 tries to like it
    other_email = "other@example.com"
    other_pass = "pass"
    create_res2 = await client.post("/v1/accounts", json={"name": "Other", "email": other_email, "password": other_pass})
    assert create_res2.status_code == 200, f"User2 creation failed: {create_res2.json()}"
    await asyncio.sleep(5)
    login2 = await client.post("/v1/accounts/login", data={"username": other_email, "password": other_pass, "grant_type": "password"})
    assert login2.status_code == 200, f"Login2 failed: {login2.json()}"
    token2 = login2.json().get("access_token")
    assert token2

    res = await client.post(f"/v1/like/{blog_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403
    assert res.json()["detail"] == "You cannot like a private post you don't own"
