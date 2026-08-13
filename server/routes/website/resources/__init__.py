from fastapi import APIRouter

from .website import WEBSITE_RESOURCE_ROUTER


RESOURCE_ROUTER = APIRouter(prefix="/resource", tags=["resource"])
RESOURCE_ROUTER.include_router(WEBSITE_RESOURCE_ROUTER)

__all__ = ["RESOURCE_ROUTER"]
