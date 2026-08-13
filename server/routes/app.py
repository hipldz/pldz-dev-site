from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core import ProjectConfig


from .identity import AUTH_ROUTER
from .operations import CACHE_ROUTER, WWW_DEPLOY_ROUTER
from .website import (
    ANALYTICS_ROUTER,
    RESOURCE_ROUTER,
    ARTICLES_ROUTER,
    IMAGES_ROUTER,
    COMMENTS_ROUTER,
    WHITEBOARD_ROUTER,
    LIVEDEMO_ROUTER,
)


# 生命周期具体执行的内容
@asynccontextmanager
async def lifespan(app=FastAPI):
    yield

# 设置生命周期的行为
app = FastAPI(lifespan=lifespan)
# 挂载路由

app.include_router(AUTH_ROUTER, prefix="/api/v1")
app.include_router(CACHE_ROUTER, prefix="/api/v1")
app.include_router(RESOURCE_ROUTER, prefix="/api/v1")
app.include_router(ANALYTICS_ROUTER, prefix="/api/v1")
app.include_router(WWW_DEPLOY_ROUTER, prefix="/api/v1")

app.include_router(ARTICLES_ROUTER, prefix="/api/v1")
app.include_router(IMAGES_ROUTER, prefix="/api/v1")
app.include_router(COMMENTS_ROUTER, prefix="/api/v1")
app.include_router(WHITEBOARD_ROUTER, prefix="/api/v1")
app.include_router(LIVEDEMO_ROUTER, prefix="/api/v1")


def run_dev():
    '''
    启动fastapi webserver 服务
    '''
    settings = ProjectConfig.get_settings()

    uvicorn.run(app, host=settings.site_host, port=settings.site_port)
