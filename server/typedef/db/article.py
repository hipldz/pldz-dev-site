from typing import NotRequired, TypedDict


class ArticleMeta(TypedDict, total=False):
    title: str
    author: str
    category: str
    serialNo: int
    status: str
    tags: list[str]
    date: str
    thumbnail: str
    summary: str
    csdn: str
    juejin: str
    github: str
    gitee: str


class ArticleIndexRecord(TypedDict):
    """Article metadata enriched with persistent views at the storage boundary."""

    id: str
    path: str
    meta: ArticleMeta
    views: NotRequired[int]
    content: NotRequired[str]
