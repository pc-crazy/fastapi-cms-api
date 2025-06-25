# tests/test_blog.py
def create_and_auth_user(client, email="author@example.com", password="authorpass"):
    client.post("/accounts", json={
        "name": "Author",
        "email": email,
        "password": password
    })
    res = client.post("/accounts/login", data={
        "username": email,
        "password": password,
        "grant_type": "password"
    })
    return res.json()["access_token"]

def test_create_blog(client):
    token = create_and_auth_user(client)
    response = client.post("/blog", json={
        "title": "Test Blog",
        "description": "Short desc",
        "content": "Blog content",
        "is_public": True
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Blog"

def test_get_blog_by_id(client):
    token = create_and_auth_user(client, "reader@example.com", "readpass")
    create_res = client.post("/blog", json={
        "title": "Get Blog",
        "description": "Read me",
        "content": "Read content",
        "is_public": True
    }, headers={"Authorization": f"Bearer {token}"})
    blog_id = create_res.json()["id"]

    get_res = client.get(f"/blog/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Get Blog"

def test_update_blog(client):
    token = create_and_auth_user(client)
    create = client.post("/blog", json={
        "title": "To Update",
        "description": "Old",
        "content": "Old content",
        "is_public": True
    }, headers={"Authorization": f"Bearer {token}"})
    blog_id = create.json()["id"]
    update = client.put(f"/blog/{blog_id}", json={
        "title": "Updated",
        "description": "New desc",
        "content": "Updated content",
        "is_public": False
    }, headers={"Authorization": f"Bearer {token}"})
    assert update.status_code == 200
    assert update.json()["title"] == "Updated"

def test_delete_blog(client):
    token = create_and_auth_user(client)
    create = client.post("/blog", json={
        "title": "Delete Me",
        "description": "Del",
        "content": "Del content",
        "is_public": True
    }, headers={"Authorization": f"Bearer {token}"})
    blog_id = create.json()["id"]
    delete = client.delete(f"/blog/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == 200
    assert delete.json()["message"] == "Post deleted"

def test_get_all_blogs(client):
    token = create_and_auth_user(client)
    # create one public, one private
    client.post("/blog", json={"title": "Pub", "description": "desc", "content": "pub content", "is_public": True}, headers={"Authorization": f"Bearer {token}"})
    client.post("/blog", json={"title": "Priv", "description": "desc", "content": "priv content", "is_public": False}, headers={"Authorization": f"Bearer {token}"})
    res = client.get("/blog", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) == 2

def test_get_private_blog_denied(client):
    token1 = create_and_auth_user(client, "owner@example.com")
    post = client.post("/blog", json={"title": "Private", "description": "desc", "content": "priv content", "is_public": False}, headers={"Authorization": f"Bearer {token1}"})
    post_id = post.json()["id"]
    token2 = create_and_auth_user(client, "intruder@example.com")
    res = client.get(f"/blog/{post_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403