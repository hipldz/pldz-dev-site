from storage.db.json_store import (
    JsonStoreError,
    _lock,
    _read_json,
    _write_json,
    get_article_views_db_path,
)


class ArticleViewStore:
    """Persistent counters that cannot be rebuilt from Markdown content."""

    @staticmethod
    def read() -> dict[str, int]:
        with _lock:
            views = _read_json(get_article_views_db_path())
        if not isinstance(views, dict):
            raise JsonStoreError("Article views DB root must be an object")
        return {str(article_id): max(0, int(count)) for article_id, count in views.items()}

    @staticmethod
    def increment(article_id: str) -> int:
        with _lock:
            path = get_article_views_db_path()
            views = _read_json(path)
            next_count = max(0, int(views.get(article_id, 0))) + 1
            views[article_id] = next_count
            _write_json(path, views)
        return next_count
