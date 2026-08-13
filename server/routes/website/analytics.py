from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from services.website.analytics import AnalyticsService
from routes.dependencies import current_user, ensure_admin_user

ANALYTICS_ROUTER = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_request_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "").strip()
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip

    return request.client.host if request.client else "0.0.0.0"


def _ensure_admin(user: dict) -> dict:
    return ensure_admin_user(
        user,
        login_detail="未授权访问，请先登录。",
        forbidden_detail="您没有权限访问该统计数据。",
    )


class AnalyticsTrackRequest(BaseModel):
    event_name: str = Field(..., description="page_view/article_view/cta_impression/cta_click")
    path: str = ""
    event_key: str = ""
    event_source: str = ""
    article_id: str = ""
    article_title: str = ""
    referrer: str = ""
    client_user_agent: str = ""
    extra: dict = Field(default_factory=dict)


@ANALYTICS_ROUTER.post("/track")
async def api_track_event(payload: AnalyticsTrackRequest, request: Request):
    user_agent = request.headers.get("user-agent", "") or payload.client_user_agent
    ip = _get_request_ip(request)
    data = AnalyticsService.track_event(
        event_name=payload.event_name,
        path=payload.path,
        event_key=payload.event_key,
        event_source=payload.event_source,
        article_id=payload.article_id,
        article_title=payload.article_title,
        referrer=payload.referrer,
        ip=ip,
        user_agent=user_agent,
        extra=payload.extra,
    )
    return {"data": data}


@ANALYTICS_ROUTER.get("/overview")
async def api_analytics_overview(
    range_value: str = "30d",
    granularity: str = "day",
    user: dict = Depends(current_user),
):
    _ensure_admin(user)
    return {"data": AnalyticsService.get_overview(range_value=range_value, granularity=granularity)}


@ANALYTICS_ROUTER.get("/articles/top")
async def api_analytics_top_articles(
    range_value: str = "30d",
    limit: int = 10,
    user: dict = Depends(current_user),
):
    _ensure_admin(user)
    return {"data": AnalyticsService.get_top_articles(range_value=range_value, limit=limit)}


@ANALYTICS_ROUTER.get("/cta")
async def api_analytics_cta(
    range_value: str = "30d",
    event_key: str = "live_demo",
    user: dict = Depends(current_user),
):
    _ensure_admin(user)
    return {"data": AnalyticsService.get_cta_summary(range_value=range_value, event_key=event_key)}
