from datetime import datetime, timedelta, timezone

import jwt

from core import ProjectConfig
from services.website.article import ArticleService


AUDIENCE = "draft-share"
ALGORITHM = "HS256"


class DraftShareError(Exception):
    """A share is invalid or its draft is no longer available."""


class DraftShareExpiredError(DraftShareError):
    """A correctly signed share has reached its expiration time."""


def _get_draft(article_id: str) -> dict:
    article = ArticleService.get_draft_by_id(article_id)
    if not article:
        raise DraftShareError("草稿不存在或已发布")
    return article


def create_draft_share(article_id: str, duration_minutes: int) -> dict:
    _get_draft(article_id)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=duration_minutes)
    token = jwt.encode(
        {"sub": article_id, "aud": AUDIENCE, "iat": now, "exp": expires_at},
        ProjectConfig.get_settings().secret_key,
        algorithm=ALGORITHM,
    )
    return {"token": token, "expiresAt": expires_at.replace(microsecond=0).isoformat()}


def get_shared_draft(article_id: str, token: str) -> dict:
    try:
        claims = jwt.decode(
            token,
            ProjectConfig.get_settings().secret_key,
            algorithms=[ALGORITHM],
            audience=AUDIENCE,
            options={"require": ["sub", "aud", "iat", "exp"]},
        )
        if claims["sub"] != article_id:
            raise jwt.InvalidTokenError("Article does not match share token")
        expires_at = datetime.fromtimestamp(claims["exp"], timezone.utc).isoformat()
    except jwt.ExpiredSignatureError as error:
        raise DraftShareExpiredError("分享链接已过期") from error
    except (jwt.InvalidTokenError, ValueError, OverflowError) as error:
        raise DraftShareError("分享链接无效") from error
    return {"article": _get_draft(article_id), "expiresAt": expires_at}
