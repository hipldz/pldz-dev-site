import os
from pathlib import PurePosixPath
from typing import List, Optional

from core import ProjectConfig
from storage.cache.website.article_index import ArticleIndexStore
from storage.db.website.article_views import ArticleViewStore
from typedef import ArticleIndexRecord, TagCount

ARTICLES_DIR = ProjectConfig.get_articles_path()


def _is_published(doc: ArticleIndexRecord) -> bool:
    return doc.get("meta", {}).get("status") == "publish"


def _is_draft(doc: ArticleIndexRecord) -> bool:
    path = str(doc.get("path", "")).replace("\\", "/")
    parts = PurePosixPath(path).parts
    return bool(parts and parts[0].lower() == ".cache")


def _is_visible(doc: ArticleIndexRecord) -> bool:
    if _is_draft(doc):
        return False
    return _is_published(doc)


def _read_content(path: str) -> str:
    from storage.resource.website.article import ArticleResourceStore

    full_path = os.path.join(ARTICLES_DIR, path)
    file_doc = ArticleResourceStore.get_file_doc(full_path)
    return file_doc["content"] if file_doc else ""


def _articles_with_views() -> list[ArticleIndexRecord]:
    index = ArticleIndexStore.read()
    views = ArticleViewStore.read()
    return [
        dict(article, views=views.get(article_id, 0), isDraft=_is_draft(article))
        for article_id, article in index.items()
    ]


def find_drafts() -> list[ArticleIndexRecord]:
    docs = [article for article in _articles_with_views() if _is_draft(article)]
    docs.sort(key=lambda article: article.get("meta", {}).get("date", ""), reverse=True)
    return docs


def find_draft_by_id(article_id: str) -> Optional[ArticleIndexRecord]:
    doc = ArticleIndexStore.read().get(article_id)
    if not doc or not _is_draft(doc):
        return None
    return dict(doc, isDraft=True, content=_read_content(doc["path"]))


def find_all_articles() -> List[ArticleIndexRecord]:
    docs = [
        article
        for article in _articles_with_views()
        if _is_visible(article) and article.get("meta", {}).get("serialNo", 0) != 0
    ]
    docs.sort(key=lambda article: article.get("meta", {}).get("date", ""), reverse=True)
    return docs


def find_article_intros() -> List[ArticleIndexRecord]:
    docs = [
        article
        for article in _articles_with_views()
        if _is_visible(article) and article.get("meta", {}).get("serialNo", 0) == 0
    ]
    docs.sort(key=lambda article: article.get("meta", {}).get("category", ""))
    return docs


def find_article_by_id(article_id: str) -> Optional[ArticleIndexRecord]:
    doc = ArticleIndexStore.read().get(article_id)
    if not doc or not _is_visible(doc):
        return None

    result = dict(doc)
    result["views"] = ArticleViewStore.increment(article_id)
    result["isDraft"] = _is_draft(doc)
    result["content"] = _read_content(doc["path"])
    return result


def find_all_categories() -> list[str]:
    return list({
        article["meta"]["category"]
        for article in _articles_with_views()
        if _is_visible(article) and "category" in article.get("meta", {})
    })


def find_articles_by_category(category: str) -> list[ArticleIndexRecord]:
    articles = [
        article
        for article in _articles_with_views()
        if _is_visible(article)
        and article.get("meta", {}).get("category") == category
        and article.get("meta", {}).get("serialNo", 0) != 0
    ]
    articles.sort(key=lambda article: article.get("meta", {}).get("serialNo", 0))
    return articles


def find_all_tag_and_counts() -> list[TagCount]:
    counts: dict[str, int] = {}
    for article in _articles_with_views():
        if not _is_visible(article):
            continue
        for tag in article.get("meta", {}).get("tags", []):
            counts[tag] = counts.get(tag, 0) + 1
    return [TagCount(text=tag, size=count) for tag, count in counts.items()]


def find_articles_by_tag(tag: str) -> list[ArticleIndexRecord]:
    articles = [
        article
        for article in _articles_with_views()
        if _is_visible(article)
        and tag in article.get("meta", {}).get("tags", [])
        and article.get("meta", {}).get("serialNo", 0) != 0
    ]
    articles.sort(key=lambda article: article.get("meta", {}).get("date", ""), reverse=True)
    return articles
