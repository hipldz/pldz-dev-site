import pytest

from services.identity.authorization import ADMIN_USERNAME, AuthenticationError, AuthorizationService
from storage.cache.website.article_index import ArticleIndexStore
from storage.db.website.article_views import ArticleViewStore


@pytest.fixture
def draft_index(monkeypatch):
    articles = {
        "published": {"id": "published", "path": "public/post.md", "meta": {
            "status": "publish", "serialNo": 1, "category": "public", "tags": ["public"]}},
        "intro": {"id": "intro", "path": "public/ABOUT.md", "meta": {
            "status": "publish", "serialNo": 0, "category": "public"}},
        "draft": {"id": "draft", "path": ".cache/post.md", "meta": {
            "status": "publish", "serialNo": 1, "category": "private", "tags": ["private"]}},
        "draft-intro": {"id": "draft-intro", "path": ".cache\\ABOUT.md", "meta": {
            "status": "draft", "serialNo": 0, "category": "private"}},
    }
    monkeypatch.setattr(ArticleIndexStore, "read", classmethod(lambda cls: articles))
    monkeypatch.setattr(ArticleViewStore, "read", classmethod(lambda cls: {}))

    def no_increment(cls, article_id):
        pytest.fail("Draft previews must not increment article views")

    monkeypatch.setattr(ArticleViewStore, "increment", classmethod(no_increment))
    monkeypatch.setattr("storage.db.website.article._read_content", lambda path: "Draft body")

    def user_from_token(cls, token):
        if token == "admin":
            return {"username": ADMIN_USERNAME}
        if token == "member":
            return {"username": "ordinary-member"}
        raise AuthenticationError("Not logged in")

    monkeypatch.setattr(AuthorizationService, "get_user_from_access_token", classmethod(user_from_token))


@pytest.mark.parametrize("role", [None, "member", "admin"])
def test_website_never_includes_drafts(client, draft_index, role):
    if role:
        client.cookies.set("access_token", role)
    prefix = "/api/v1/website/article"
    for path in ("/all/article", "/category/public", "/tag/public"):
        assert [item["id"] for item in client.get(prefix + path).json()["data"]] == ["published"]
    assert [item["id"] for item in client.get(prefix + "/all/intro").json()["data"]] == ["intro"]
    assert client.get(prefix + "/all/category").json()["data"] == ["public"]
    assert client.get(prefix + "/all/tag").json()["data"] == [{"text": "public", "size": 1}]
    assert client.get(prefix + "/category/private").json()["data"] == []
    assert client.get(prefix + "/tag/private").json()["data"] == []
    for article_id in ("draft", "draft-intro"):
        assert client.get(prefix + "/id/" + article_id).json()["data"] is None


@pytest.mark.parametrize("role,status", [(None, 401), ("member", 403), ("admin", 200)])
def test_draft_endpoints_require_admin(client, draft_index, role, status):
    if role:
        client.cookies.set("access_token", role)
    for path in ("/drafts", "/draft/draft"):
        response = client.get("/api/v1/website/article" + path)
        assert response.status_code == status
        if status == 200 and path == "/drafts":
            assert {item["id"] for item in response.json()["data"]} == {"draft", "draft-intro"}
            assert all(item["isDraft"] for item in response.json()["data"])


def test_draft_preview_is_private_and_does_not_count_views(client, draft_index):
    client.cookies.set("access_token", "admin")
    prefix = "/api/v1/website/article/draft/"
    result = client.get(prefix + "draft").json()["data"]
    assert result["isDraft"] is True
    assert result["content"] == "Draft body"
    assert client.get(prefix + "published").status_code == 404
    assert client.get(prefix + "missing").status_code == 404
