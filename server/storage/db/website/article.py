import os
from typing import List, Optional

from core import ProjectConfig
from storage.cache.website.article_index import ArticleIndexStore
from storage.db.website.article_views import ArticleViewStore
from typedef import ArticleIndexRecord, TagCount

ARTICLES_DIR = ProjectConfig.get_articles_path()


def _is_published(doc: ArticleIndexRecord) -> bool:
    return doc.get("meta", {}).get("status") == "publish"


def _read_content(path: str) -> str:
    from storage.resource.website.article import ArticleResourceStore

    full_path = os.path.join(ARTICLES_DIR, path)
    file_doc = ArticleResourceStore.get_file_doc(full_path)
    return file_doc["content"] if file_doc else ""


def _articles_with_views() -> list[ArticleIndexRecord]:
    index = ArticleIndexStore.read()
    views = ArticleViewStore.read()
    return [dict(article, views=views.get(article_id, 0)) for article_id, article in index.items()]


def find_all_articles() -> List[ArticleIndexRecord]:
    docs = [
        article
        for article in _articles_with_views()
        if _is_published(article) and article.get("meta", {}).get("serialNo", 0) != 0
    ]
    docs.sort(key=lambda article: article.get("meta", {}).get("date", ""), reverse=True)
    return docs


def find_article_intros() -> List[ArticleIndexRecord]:
    docs = [
        article
        for article in _articles_with_views()
        if _is_published(article) and article.get("meta", {}).get("serialNo", 0) == 0
    ]
    docs.sort(key=lambda article: article.get("meta", {}).get("category", ""))
    return docs


def find_article_by_id(article_id: str) -> Optional[ArticleIndexRecord]:
    doc = ArticleIndexStore.read().get(article_id)
    if not doc or not _is_published(doc):
        return None

    result = dict(doc)
    result["views"] = ArticleViewStore.increment(article_id)
    result["content"] = _read_content(doc["path"])
    return result


def find_all_categories() -> list[str]:
    return list({
        article["meta"]["category"]
        for article in _articles_with_views()
        if _is_published(article) and "category" in article.get("meta", {})
    })


def find_articles_by_category(category: str) -> list[ArticleIndexRecord]:
    articles = [
        article
        for article in _articles_with_views()
        if _is_published(article)
        and article.get("meta", {}).get("category") == category
        and article.get("meta", {}).get("serialNo", 0) != 0
    ]
    articles.sort(key=lambda article: article.get("meta", {}).get("serialNo", 0))
    return articles


def find_all_tag_and_counts() -> list[TagCount]:
    counts: dict[str, int] = {}
    for article in _articles_with_views():
        if not _is_published(article):
            continue
        for tag in article.get("meta", {}).get("tags", []):
            counts[tag] = counts.get(tag, 0) + 1
    return [TagCount(text=tag, size=count) for tag, count in counts.items()]


def find_articles_by_tag(tag: str) -> list[ArticleIndexRecord]:
    articles = [
        article
        for article in _articles_with_views()
        if _is_published(article)
        and tag in article.get("meta", {}).get("tags", [])
        and article.get("meta", {}).get("serialNo", 0) != 0
    ]
    articles.sort(key=lambda article: article.get("meta", {}).get("date", ""), reverse=True)
    return articles
