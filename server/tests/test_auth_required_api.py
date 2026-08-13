def assert_requires_login(response):
    assert response.status_code == 401


def test_cache_all_requires_login(client):
    assert_requires_login(client.get("/api/v1/cache/all"))


def test_cache_delete_requires_login(client):
    assert_requires_login(
        client.post("/api/v1/cache/delete", json={"filename": "x.txt"})
    )


def test_cache_download_requires_login(client):
    assert_requires_login(
        client.post("/api/v1/cache/download", json={"filename": "x.txt"})
    )


def test_cache_upload_requires_login(client):
    assert_requires_login(
        client.post(
            "/api/v1/cache/upload",
            files={"file": ("x.txt", b"hello", "text/plain")},
        )
    )


def test_cache_file_get_requires_machine_token(client):
    assert client.get("/api/v1/cache/files/x.txt").status_code == 403


def test_cache_file_put_requires_machine_token(client):
    assert (
        client.put(
            "/api/v1/cache/files/x.txt",
            content=b"hello",
            headers={"content-length": "5"},
        ).status_code
        == 403
    )


def test_cache_raw_requires_admin(client):
    assert_requires_login(client.get("/api/v1/cache/raw/x.txt"))


def test_livedemo_set_requires_login(client):
    assert_requires_login(client.post("/api/v1/website/livedemo/set", json={"data": []}))


def test_image_category_all_requires_login(client):
    assert_requires_login(
        client.post("/api/v1/website/image/category/all", json={"category": "avatar"})
    )


def test_image_upload_check_requires_login(client):
    assert_requires_login(
        client.post(
            "/api/v1/website/image/upload/check",
            json={"category": "avatar", "name": "default.jpg"},
        )
    )


def test_image_upload_avatar_requires_login(client):
    assert_requires_login(
        client.post(
            "/api/v1/website/image/upload/avatar",
            data={"name": "avatar.jpg"},
            files={"file": ("avatar.jpg", b"not-an-image", "image/jpeg")},
        )
    )


def test_image_upload_article_requires_login(client):
    assert_requires_login(
        client.post(
            "/api/v1/website/image/upload/article",
            data={"category": "avatar", "name": "article.jpg"},
            files={"file": ("article.jpg", b"not-an-image", "image/jpeg")},
        )
    )


def test_image_delete_requires_login(client):
    assert_requires_login(
        client.post(
            "/api/v1/website/image/delete",
            json={"category": "avatar", "name": "default.jpg"},
        )
    )


def test_image_rename_requires_login(client):
    assert_requires_login(
        client.post(
            "/api/v1/website/image/rename",
            json={
                "category": "avatar",
                "oldName": "default.jpg",
                "newName": "renamed.jpg",
            },
        )
    )


def test_comment_add_requires_login(client):
    assert_requires_login(
        client.post(
            "/api/v1/website/comment/add",
            json={"article_id": "x", "content": {}, "parent_id": ""},
        )
    )


def test_comment_delete_requires_login(client):
    assert_requires_login(
        client.post(
            "/api/v1/website/comment/delete",
            json={"article_id": "x", "comment_id": "y"},
        )
    )


def test_two_factor_setup_requires_login(client):
    assert_requires_login(client.post("/api/v1/authorization/2fa/setup"))


def test_two_factor_confirm_requires_login(client):
    assert_requires_login(
        client.post("/api/v1/authorization/2fa/confirm", json={"code": "000000"})
    )


def test_two_factor_disable_requires_login(client):
    assert_requires_login(
        client.post("/api/v1/authorization/2fa/disable", json={"code": "000000"})
    )


def test_update_avatar_requires_login(client):
    assert_requires_login(
        client.post("/api/v1/authorization/update/avatar", json={"avatar": "/x.jpg"})
    )


def test_user_management_all_requires_login(client):
    assert_requires_login(client.get("/api/v1/authorization/usermanagement/all"))


def test_user_management_delete_requires_login(client):
    assert_requires_login(
        client.post(
            "/api/v1/authorization/usermanagement/delete",
            json={"username": "user@example.com"},
        )
    )


def test_analytics_overview_requires_login(client):
    assert_requires_login(client.get("/api/v1/analytics/overview"))


def test_analytics_top_articles_requires_login(client):
    assert_requires_login(client.get("/api/v1/analytics/articles/top"))


def test_analytics_cta_requires_login(client):
    assert_requires_login(client.get("/api/v1/analytics/cta"))


def test_www_deployments_all_requires_login(client):
    assert_requires_login(client.get("/api/v1/deploy/www/all"))


def test_www_deployments_retry_requires_login(client):
    assert_requires_login(client.post("/api/v1/deploy/www/retry", json={"id": "missing"}))
