def assert_data_response(response):
    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    return payload["data"]


def test_authorization_privacy(client):
    data = assert_data_response(client.get("/api/v1/authorization/privacy"))

    assert set(data) >= {"icp", "copyright", "ps"}


def test_authorization_logout_without_cookie(client):
    data = assert_data_response(client.get("/api/v1/authorization/logout"))

    assert data is True


def test_authorization_login_rejects_unknown_user(client):
    data = assert_data_response(
        client.post(
            "/api/v1/authorization/login",
            json={"username": "missing@example.com", "password": "bad"},
        )
    )

    assert data["flag"] is False


def test_authorization_register_success_sets_cookie(client, monkeypatch):
    from routes.identity import authorization

    created_user = {
        "id": "pytest-user-id",
        "username": "pytest-register@example.com",
        "nickname": "pytest",
        "avatar": "/avatar.jpg",
        "isadmin": False,
        "two_factor_enabled": False,
    }

    monkeypatch.setattr(
        authorization.AuthorizationService,
        "get_user_by_username",
        lambda username: None if not hasattr(test_authorization_register_success_sets_cookie, "created") else created_user,
    )
    monkeypatch.setattr(
        authorization.AuthorizationService,
        "add_user",
        lambda username, password, nickname: setattr(test_authorization_register_success_sets_cookie, "created", True) or True,
    )
    monkeypatch.setattr(
        authorization.AuthorizationService,
        "create_access_token",
        lambda username: "access-token",
    )
    monkeypatch.setattr(
        authorization.AuthorizationService,
        "create_refresh_token",
        lambda username: "refresh-token",
    )

    response = client.post(
        "/api/v1/authorization/register",
        json={
            "username": "pytest-register@example.com",
            "password": "secret123",
            "nickname": "pytest",
        },
    )
    data = assert_data_response(response)

    assert data["flag"] is True
    assert "access_token" in client.cookies
    refresh_cookie = next(
        header for header in response.headers.get_list("set-cookie")
        if header.startswith("refresh_token=")
    )
    assert f"Max-Age={authorization.REFRESH_EXPIRE.days * 86400}" in refresh_cookie


def test_authorization_register_rejects_weak_payload(client):
    response = client.post(
        "/api/v1/authorization/register",
        json={"username": "x", "password": "short", "nickname": ""},
    )

    assert response.status_code == 422


def test_authorization_refresh_requires_cookie(client):
    response = client.post("/api/v1/authorization/refresh")

    assert response.status_code == 401


def test_article_all_categories(client):
    data = assert_data_response(client.get("/api/v1/website/article/all/category"))

    assert isinstance(data, list)


def test_article_all_articles(client):
    data = assert_data_response(client.get("/api/v1/website/article/all/article"))

    assert isinstance(data, list)


def test_article_all_intros(client):
    data = assert_data_response(client.get("/api/v1/website/article/all/intro"))

    assert isinstance(data, list)


def test_article_all_tags(client):
    data = assert_data_response(client.get("/api/v1/website/article/all/tag"))

    assert isinstance(data, list)


def test_article_unknown_category_returns_empty_list(client):
    data = assert_data_response(client.get("/api/v1/website/article/category/__missing__"))

    assert data == []


def test_article_unknown_tag_returns_empty_list(client):
    data = assert_data_response(client.get("/api/v1/website/article/tag/__missing__"))

    assert data == []


def test_article_by_id(client):
    articles = assert_data_response(client.get("/api/v1/website/article/all/article"))
    assert articles

    data = assert_data_response(client.get(f"/api/v1/website/article/id/{articles[0]['id']}"))

    assert data["id"] == articles[0]["id"]
    assert "content" in data


def test_livedemo_all(client):
    data = assert_data_response(client.get("/api/v1/website/livedemo/all"))

    assert isinstance(data, list)
    if data:
        assert set(data[0]) >= {"title", "url", "thumbnail", "previewgif"}


def test_resource_raw_file(client):
    response = client.get("/api/v1/resource/website/config/navigation.json")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


def test_resource_privacy_policy_page(client):
    response = client.get("/api/v1/resource/website/legal/privacy-policy")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_resource_user_agreement_page(client):
    response = client.get("/api/v1/resource/website/legal/user-agreement")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_resource_raw_missing_file(client):
    response = client.get("/api/v1/resource/website/__missing__.json")

    assert response.status_code == 404


def test_resource_raw_rejects_path_traversal(client):
    response = client.get("/api/v1/resource/%2E%2E/.env")

    assert response.status_code in (403, 404)


def test_cache_public_missing_file(client):
    response = client.get("/api/v1/cache/__missing__.txt")

    assert response.status_code == 404


def test_cache_openapi_uses_top_level_namespace(client):
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/v1/cache/all" in paths
    assert "/api/v1/resource/cache/all" not in paths


def test_image_original_file(client):
    response = client.get("/api/v1/website/image/avatar/default.jpg@original")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")


def test_image_default_resize(client):
    response = client.get("/api/v1/website/image/avatar/default.jpg")

    assert response.status_code == 200
    assert response.headers["content-type"] in {"image/webp", "image/jpeg"}


def test_image_square_resize(client):
    response = client.get("/api/v1/website/image/avatar/default.jpg@64")

    assert response.status_code == 200
    assert response.headers["content-type"] in {"image/webp", "image/jpeg"}


def test_image_width_height_resize(client):
    response = client.get("/api/v1/website/image/avatar/default.jpg@64x64")

    assert response.status_code == 200
    assert response.headers["content-type"] in {"image/webp", "image/jpeg"}


def test_image_rejects_invalid_dimensions(client):
    response = client.get("/api/v1/website/image/avatar/default.jpg@0x128")

    assert response.status_code == 400


def test_image_rejects_invalid_quality(client):
    response = client.get("/api/v1/website/image/avatar/default.jpg@128?quality=0")

    assert response.status_code == 400


def test_comment_all_requires_article_id(client):
    response = client.post("/api/v1/website/comment/all", json={"article_id": ""})

    assert response.status_code == 400


def test_comment_all_unknown_article_returns_list(client):
    data = assert_data_response(
        client.post("/api/v1/website/comment/all", json={"article_id": "__missing__"})
    )

    assert isinstance(data, list)


def test_whiteboard_update_and_read(client):
    missing = client.post("/api/v1/website/whiteboard/key", json={"key": "123"})
    assert missing.status_code == 404

    failed_update = assert_data_response(
        client.post(
            "/api/v1/website/whiteboard/update",
            json={"key": "123", "content": "hello pytest"},
        )
    )
    assert failed_update["flag"] is False

    items = assert_data_response(
        client.post(
            "/api/v1/website/whiteboard/authorized",
            json={"username": "pytest", "create_new": True},
        )
    )
    assert isinstance(items, list)
    assert items

    key = items[0]["key"]
    updated = assert_data_response(
        client.post(
            "/api/v1/website/whiteboard/update",
            json={"key": key, "content": "hello pytest"},
        )
    )
    assert updated["flag"] is True

    item = assert_data_response(
        client.post("/api/v1/website/whiteboard/key", json={"key": key})
    )
    assert item["content"] == "hello pytest"


def test_whiteboard_requires_key_for_lookup(client):
    response = client.post("/api/v1/website/whiteboard/key", json={"key": ""})

    assert response.status_code == 400


def test_whiteboard_requires_key_for_update(client):
    response = client.post(
        "/api/v1/website/whiteboard/update",
        json={"key": "", "content": "hello"},
    )

    assert response.status_code == 400


def test_analytics_track_requires_event_name(client):
    response = client.post("/api/v1/analytics/track", json={"path": "/"})

    assert response.status_code == 422


def test_analytics_track_success(client, monkeypatch):
    from routes.website import analytics

    def fake_track_event(**kwargs):
        return {"flag": True, "event_name": kwargs["event_name"]}

    monkeypatch.setattr(analytics.AnalyticsService, "track_event", fake_track_event)

    data = assert_data_response(
        client.post(
            "/api/v1/analytics/track",
            json={"event_name": "page_view", "path": "/"},
        )
    )

    assert data == {"flag": True, "event_name": "page_view"}
