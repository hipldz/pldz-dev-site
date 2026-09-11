from pydantic import BaseModel
from fastapi import Depends
from fastapi.routing import APIRouter
from services.website.livedemo import LiveDemoService
from routes.dependencies import current_user, ensure_admin_user

LIVEDEMO_ROUTER = APIRouter(prefix="/website/livedemo", tags=["website-livedemo"])


@LIVEDEMO_ROUTER.get("/all")
async def api_get_all_livedemo_items():
    """
    获取所有 live demo 项目
    """
    items = LiveDemoService.get_all()
    return {"data": items}


class SetLiveDemoRequest(BaseModel):
    """
    设置 livedemo 信息的请求体
    """
    # 每个字典代表一个 livedemo 项，包含 title, url, new 等字段
    data: list = []


@LIVEDEMO_ROUTER.post("/set")
async def api_set_livedemo(request: SetLiveDemoRequest, user: dict = Depends(current_user)):
    """
    设置 livedemo 信息
    """
    ensure_admin_user(
        user,
        login_detail="You must be logged in to sync articles.",
        forbidden_detail="You do not have permission to sync articles.",
    )
    flag = LiveDemoService.replace_all(request.data)
    return {"data": flag}
