from typing import TypedDict

from pydantic import BaseModel


class ArticleSummary(TypedDict):
    id: str
    title: str
    category: str
    summary: str
    serialNo: int
    thumbnail: str
    tags: list[str]
    views: int
    date: str
    path: str
    csdn: str
    juejin: str
    github: str
    gitee: str


class TagCount(TypedDict):
    text: str
    size: int


class ArticleListResponse(BaseModel):
    data: list[dict]


class CategoryListResponse(BaseModel):
    data: list[str]


class TagListResponse(BaseModel):
    data: list[dict]


class ArticleDetailResponse(BaseModel):
    data: dict | None
