from core import ProjectConfig
from storage.db.json_store import JsonStoreError, _lock, _read_json, _write_json


class ArticleIndexStore:
    """Rebuildable metadata index derived from Markdown documents."""

    @staticmethod
    def path() -> str:
        return ProjectConfig.get_article_index_path()

    @classmethod
    def read(cls) -> dict[str, dict]:
        with _lock:
            data = _read_json(cls.path())
        if not isinstance(data, dict):
            raise JsonStoreError("Article index root must be an object")
        return data

    @classmethod
    def upsert(cls, article_id: str, entry: dict) -> bool:
        with _lock:
            data = _read_json(cls.path())
            existed = article_id in data
            data[article_id] = entry
            _write_json(cls.path(), data)
        return existed

    @classmethod
    def delete(cls, article_id: str) -> dict | None:
        with _lock:
            data = _read_json(cls.path())
            removed = data.pop(article_id, None)
            if removed is not None:
                _write_json(cls.path(), data)
        return removed

    @classmethod
    def prune_paths(cls, existing_paths: set[str], normalize) -> list[tuple[str, dict]]:
        with _lock:
            data = _read_json(cls.path())
            stale_ids = [
                article_id
                for article_id, article in data.items()
                if normalize(article.get("path", "")) not in existing_paths
            ]
            removed = [(article_id, data.pop(article_id)) for article_id in stale_ids]
            if removed:
                _write_json(cls.path(), data)
        return removed
