# tests/test_blog.py
import pytest

@pytest.mark.asyncio
async def create_and_auth_user(client, email="author@example.com", password="authorpass"):
    await client.post("/v1/accounts", json={
        "name": "Author",
        "email": email,
        "password": password
    })
    res = await client.post("/v1/accounts/login", data={
        "username": email,
        "password": password,
        "grant_type": "password"
    })
    return res.json()["access_token"]

@pytest.mark.asyncio
async def test_create_blog(client):
    token = await create_and_auth_user(client)
    response = await client.post("/v1/blog", json={
        "title": "Test Blog",
        "description": "Short desc",
        "content": "Blog content",
        "is_public": True
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Blog"

@pytest.mark.asyncio
async def test_get_blog_by_id(client):
    token = await create_and_auth_user(client, "reader@example.com", "readpass")
    create_res = await client.post("/v1/blog", json={
        "title": "Get Blog",
        "description": "Read me",
        "content": "Read content",
        "is_public": True
    }, headers={"Authorization": f"Bearer {token}"})
    blog_id = create_res.json()["id"]

    get_res = await client.get(f"/v1/blog/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Get Blog"

@pytest.mark.asyncio
async def test_update_blog(client):
    token = await create_and_auth_user(client)
    create = await client.post("/v1/blog", json={
        "title": "To Update",
        "description": "Old",
        "content": "Old content",
        "is_public": True
    }, headers={"Authorization": f"Bearer {token}"})
    blog_id = create.json()["id"]
    update = await client.put(f"/v1/blog/{blog_id}", json={
        "title": "Updated",
        "description": "New desc",
        "content": "Updated content",
        "is_public": False
    }, headers={"Authorization": f"Bearer {token}"})
    assert update.status_code == 200
    assert update.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_delete_blog(client):
    token = await create_and_auth_user(client)
    create = await client.post("/v1/blog", json={
        "title": "Delete Me",
        "description": "Del",
        "content": "Del content",
        "is_public": True
    }, headers={"Authorization": f"Bearer {token}"})
    blog_id = create.json()["id"]
    delete = await client.delete(f"/v1/blog/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == 200
    assert delete.json()["message"] == "Post deleted"


@pytest.mark.asyncio
async def test_get_private_blog_denied(client):
    token1 = await create_and_auth_user(client, "owner@example.com")
    post = await client.post("/v1/blog", json={"title": "Private", "description": "desc", "content": "priv content", "is_public": False}, headers={"Authorization": f"Bearer {token1}"})
    post_id = post.json()["id"]
    token2 = await create_and_auth_user(client, "intruder@example.com")
    res = await client.get(f"/v1/blog/{post_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_get_all_blogs(client):
    # Clean up existing blogs before test
    token = await create_and_auth_user(client)
    res = await client.get("/v1/blog", headers={"Authorization": f"Bearer {token}"})
    for blog in res.json():
        await client.delete(f"/v1/blog/{blog['id']}", headers={"Authorization": f"Bearer {token}"})

    # Now test creating and retrieving
    await client.post("/v1/blog", json={"title": "Pub", "description": "desc", "content": "pub content", "is_public": True}, headers={"Authorization": f"Bearer {token}"})
    await client.post("/v1/blog", json={"title": "Priv", "description": "desc", "content": "priv content", "is_public": False}, headers={"Authorization": f"Bearer {token}"})
    res = await client.get("/v1/blog", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    titles = [post["title"] for post in res.json()]
    assert "Pub" in titles
    assert "Priv" in titles