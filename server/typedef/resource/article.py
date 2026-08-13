from typing import TypedDict

from typedef.db.article import ArticleMeta


class ArticleDocument(TypedDict):
    """Authoritative Markdown article after frontmatter parsing."""

    id: str
    path: str
    meta: ArticleMeta
    content: str
