from storage.cache.website.article_index import ArticleIndexStore
from storage.db.website.article_views import ArticleViewStore


def test_article_index_rebuild_does_not_change_persistent_views(tmp_path, monkeypatch):
    from core import ProjectConfig

    monkeypatch.setattr(ProjectConfig, "PROJECT_ROOT", str(tmp_path))
    ArticleIndexStore.upsert("article-one", {
        "id": "article-one",
        "path": "category/one.md",
        "meta": {"title": "Before"},
    })
    assert ArticleViewStore.increment("article-one") == 1

    ArticleIndexStore.upsert("article-one", {
        "id": "article-one",
        "path": "category/one.md",
        "meta": {"title": "After"},
    })

    assert ArticleViewStore.read()["article-one"] == 1
    assert ArticleIndexStore.read()["article-one"]["meta"]["title"] == "After"
