"""Serialized structures grouped by DB, resource and Website API boundaries."""

from .db import ArticleIndexRecord, ArticleMeta, CommentRecord, UserRecord
from .resource import ArticleDocument, LiveDemoResource
from .website import (
    ArticleDetailResponse,
    ArticleListResponse,
    ArticleSummary,
    CategoryListResponse,
    TagCount,
    TagListResponse,
    WhiteboardItem,
)

__all__ = [
    "ArticleMeta",
    "ArticleIndexRecord",
    "CommentRecord",
    "UserRecord",
    "ArticleDocument",
    "LiveDemoResource",
    "ArticleSummary",
    "TagCount",
    "ArticleListResponse",
    "ArticleDetailResponse",
    "CategoryListResponse",
    "TagListResponse",
    "WhiteboardItem",
]
