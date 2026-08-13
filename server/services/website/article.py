from typing import Optional
from typedef import ArticleIndexRecord, TagCount

from storage.db.website.article import (
    find_all_articles,
    find_all_categories,
    find_all_tag_and_counts,
    find_article_by_id,
    find_article_intros,
    find_articles_by_category,
    find_articles_by_tag,
)


class ArticleService:
    @classmethod
    def get_all_categories(cls) -> list[str]:
        return find_all_categories()

    @classmethod
    def get_all_articles(cls) -> list[ArticleIndexRecord]:
        return find_all_articles()

    @classmethod
    def get_article_intros(cls) -> list[ArticleIndexRecord]:
        return find_article_intros()

    @classmethod
    def get_article_by_id(cls, article_id: str) -> Optional[ArticleIndexRecord]:
        return find_article_by_id(article_id)

    @classmethod
    def get_all_tag_and_counts(cls) -> list[TagCount]:
        return find_all_tag_and_counts()

    @classmethod
    def get_articles_by_category(cls, category: str) -> list[ArticleIndexRecord]:
        return find_articles_by_category(category)

    @classmethod
    def get_articles_by_tag(cls, tag: str) -> list[ArticleIndexRecord]:
        return find_articles_by_tag(tag)
