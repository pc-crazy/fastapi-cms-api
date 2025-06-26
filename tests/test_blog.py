# tests/test_blog.py
def create_and_auth_user(
    client, email="author@example.com", password="authorpass"
):
    client.post(
        "/v1/accounts",
        json={"name": "Author", "email": email, "password": password},
    )
    res = client.post(
        "/v1/accounts/login",
        data={
            "username": email,
            "password": password,
            "grant_type": "password",
        },
    )
    return res.json()["access_token"]


def test_create_blog(client):
    token = create_and_auth_user(client)
    response = client.post(
        "/v1/blog",
        json={
            "title": "Test Blog",
            "description": "Short desc",
            "content": "Blog content",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Blog"


def test_get_blog_by_id(client):
    token = create_and_auth_user(client, "reader@example.com", "readpass")
    create_res = client.post(
        "/v1/blog",
        json={
            "title": "Get Blog",
            "description": "Read me",
            "content": "Read content",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    blog_id = create_res.json()["id"]

    get_res = client.get(
        f"/v1/blog/{blog_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Get Blog"


def test_update_blog(client):
    token = create_and_auth_user(client)
    create = client.post(
        "/v1/blog",
        json={
            "title": "To Update",
            "description": "Old",
            "content": "Old content",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    blog_id = create.json()["id"]
    update = client.put(
        f"/v1/blog/{blog_id}",
        json={
            "title": "Updated",
            "description": "New desc",
            "content": "Updated content",
            "is_public": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update.status_code == 200
    assert update.json()["title"] == "Updated"


def test_delete_blog(client):
    token = create_and_auth_user(client)
    create = client.post(
        "/v1/blog",
        json={
            "title": "Delete Me",
            "description": "Del",
            "content": "Del content",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    blog_id = create.json()["id"]
    delete = client.delete(
        f"/v1/blog/{blog_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete.status_code == 200
    assert delete.json()["message"] == "Post deleted"


def test_get_all_blogs(client):
    token = create_and_auth_user(client)
    # create one public, one private
    client.post(
        "/v1/blog",
        json={
            "title": "Pub",
            "description": "desc",
            "content": "pub content",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/v1/blog",
        json={
            "title": "Priv",
            "description": "desc",
            "content": "priv content",
            "is_public": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    res = client.get("/v1/blog", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_private_blog_denied(client):
    token1 = create_and_auth_user(client, "owner@example.com")
    post = client.post(
        "/v1/blog",
        json={
            "title": "Private",
            "description": "desc",
            "content": "priv content",
            "is_public": False,
        },
        headers={"Authorization": f"Bearer {token1}"},
    )
    post_id = post.json()["id"]
    token2 = create_and_auth_user(client, "intruder@example.com")
    res = client.get(
        f"/v1/blog/{post_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert res.status_code == 403


def test_get_nonexistent_post(client):
    token = create_and_auth_user(client)
    res = client.get(
        "/v1/blog/9999", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"


def test_update_unauthorized_post(client):
    token1 = create_and_auth_user(client, email="one@example.com")
    res = client.post(
        "/v1/blog",
        json={
            "title": "A",
            "description": "",
            "content": "",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {token1}"},
    )
    post_id = res.json()["id"]
    token2 = create_and_auth_user(client, email="two@example.com")
    update_res = client.put(
        f"/v1/blog/{post_id}",
        json={
            "title": "Hack",
            "description": "",
            "content": "",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert update_res.status_code == 403
    assert update_res.json()["detail"] == "Not authorized"


def test_delete_unauthorized_post(client):
    token1 = create_and_auth_user(client, email="three@example.com")
    res = client.post(
        "/v1/blog",
        json={
            "title": "Del",
            "description": "",
            "content": "",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {token1}"},
    )
    post_id = res.json()["id"]
    token2 = create_and_auth_user(client, email="four@example.com")
    del_res = client.delete(
        f"/v1/blog/{post_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert del_res.status_code == 403
    assert del_res.json()["detail"] == "Not authorized"
