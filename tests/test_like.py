# tests/test_like.py
def create_user_and_blog(client, email="liker@example.com", password="likepass", is_public=True):
    client.post("/accounts", json={
        "name": "Liker",
        "email": email,
        "password": password
    })
    login = client.post("/accounts/login", data={
        "username": email,
        "password": password,
        "grant_type": "password"
    })
    token = login.json()["access_token"]
    post = client.post("/blog", json={
        "title": "Like Test",
        "description": "Test desc",
        "content": "Test content",
        "is_public": is_public
    }, headers={"Authorization": f"Bearer {token}"})
    return token, post.json()["id"]

def test_like_post(client):
    token, blog_id = create_user_and_blog(client)
    like_res = client.post(f"/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert like_res.status_code == 200
    assert like_res.json()["message"] == "Post liked"

def test_like_post_twice(client):
    token, blog_id = create_user_and_blog(client, email="liketwice@example.com")
    client.post(f"/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    like_again = client.post(f"/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert like_again.status_code == 400
    assert like_again.json()["detail"] == "You have already liked this post."

def test_unlike_post(client):
    token, blog_id = create_user_and_blog(client, email="unliker@example.com")
    client.post(f"/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    unlike_res = client.delete(f"/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert unlike_res.status_code == 200
    assert unlike_res.json()["message"] == "Post unliked"

def test_unlike_post_not_liked(client):
    token, blog_id = create_user_and_blog(client, email="nolike@example.com")
    unlike_res = client.delete(f"/like/{blog_id}", headers={"Authorization": f"Bearer {token}"})
    assert unlike_res.status_code == 400
    assert unlike_res.json()["detail"] == "You have not liked this post"

def test_like_invalid_post(client):
    token, _ = create_user_and_blog(client, email="invalidlike@example.com")
    res = client.post("/like/9999", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"

def test_unlike_invalid_post(client):
    token, _ = create_user_and_blog(client, email="invalidunlike@example.com")
    res = client.delete("/like/9999", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Post not found"

def test_like_private_post_not_owner(client):
    # User1 creates private post
    token1, blog_id = create_user_and_blog(client, email="owner@example.com", is_public=False)
    # User2 tries to like it
    client.post("/accounts", json={"name": "Other", "email": "other@example.com", "password": "pass"})
    login = client.post("/accounts/login", data={"username": "other@example.com", "password": "pass", "grant_type": "password"})
    token2 = login.json()["access_token"]
    res = client.post(f"/like/{blog_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403
    assert res.json()["detail"] == "You cannot like a private post you don't own"