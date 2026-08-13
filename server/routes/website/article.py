from fastapi import APIRouter

from services.website.article import ArticleService
from typedef import (
    ArticleDetailResponse,
    ArticleIndexRecord,
    ArticleListResponse,
    ArticleSummary,
    CategoryListResponse,
    TagListResponse,
)


ARTICLES_ROUTER = APIRouter(prefix="/website/article", tags=["website-article"])


def _to_summary(article: ArticleIndexRecord) -> ArticleSummary:
    meta = article.get("meta", {})
    return ArticleSummary(
        id=article.get("id", ""),
        title=meta.get("title", ""),
        category=meta.get("category", ""),
        summary=meta.get("summary", ""),
        serialNo=meta.get("serialNo", 0),
        thumbnail=meta.get("thumbnail", ""),
        tags=meta.get("tags", []),
        views=article.get("views", 0),
        date=meta.get("date", ""),
        path=article.get("path", ""),
        csdn=meta.get("csdn", ""),
        juejin=meta.get("juejin", ""),
        github=meta.get("github", ""),
        gitee=meta.get("gitee", ""),
    )


def _summaries(articles: list[ArticleIndexRecord]) -> ArticleListResponse:
    return ArticleListResponse(data=[_to_summary(article) for article in articles])


@ARTICLES_ROUTER.get("/all/category")
async def get_all_categories():
    return CategoryListResponse(data=ArticleService.get_all_categories())


@ARTICLES_ROUTER.get("/all/article")
async def get_all_articles():
    return _summaries(ArticleService.get_all_articles())


@ARTICLES_ROUTER.get("/all/intro")
async def get_article_intros():
    return _summaries(ArticleService.get_article_intros())


@ARTICLES_ROUTER.get("/all/tag")
async def get_all_tags():
    return TagListResponse(data=ArticleService.get_all_tag_and_counts())


@ARTICLES_ROUTER.get("/id/{article_id}")
async def get_article_by_id(article_id: str):
    return ArticleDetailResponse(data=ArticleService.get_article_by_id(article_id))


@ARTICLES_ROUTER.get("/tag/{tag_name}")
async def get_articles_by_tag(tag_name: str):
    return _summaries(ArticleService.get_articles_by_tag(tag_name))


@ARTICLES_ROUTER.get("/category/{category_name}")
async def get_articles_by_category(category_name: str):
    return _summaries(ArticleService.get_articles_by_category(category_name))
