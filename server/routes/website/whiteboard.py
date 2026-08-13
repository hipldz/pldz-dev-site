from pydantic import BaseModel
from typing import Optional, Any
from fastapi import HTTPException, Request, status
from fastapi.routing import APIRouter
from services.website.whiteboard import WhiteboardService
from routes.dependencies import optional_current_user

WHITEBOARD_ROUTER = APIRouter(prefix="/website/whiteboard", tags=["website-whiteboard"])


"""
==========================
Get Whiteboard by Key
==========================
"""


class GetWhiteboardByKeyRequest(BaseModel):
    key: str


@WHITEBOARD_ROUTER.post("/key")
async def api_get_whiteboard_by_key(request: GetWhiteboardByKeyRequest):
    """
    根据键获取白板内容
    """
    if not request.key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key is required."
        )

    item = WhiteboardService.get_item_by_key(request.key)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard item not found."
        )

    return {"data": item}


"""
===========================
Get Whiteboard by Username
===========================
"""


class GetWhiteboardByUsernameRequest(BaseModel):
    username: Optional[str] = None
    create_new: bool = True


@WHITEBOARD_ROUTER.post("/authorized")
async def api_get_whiteboard_by_username(request: GetWhiteboardByUsernameRequest, fastapi_request: Request):
    """
    获取当前用户（或指定用户名）的白板内容列表
    """
    username = (request.username or "").strip()

    if not username:
        user = optional_current_user(fastapi_request)
        username = user.get('username', '') if user else ""

    items = WhiteboardService.get_items_by_username(username, create_new=request.create_new)
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Whiteboard items not found."
        )

    return {"data": items}


"""
=========================
Update Request and Response Models
=========================
"""


class UpdateRequest(BaseModel):
    key: str
    content: str


class UpdateResponseData(BaseModel):
    flag: bool
    log: str
    created: Optional[Any] = None


class UpdateResponse(BaseModel):
    data: UpdateResponseData


@WHITEBOARD_ROUTER.post("/update")
async def api_update_whiteboard_content(request: UpdateRequest) -> UpdateResponse:
    """
    更新白板内容
    """
    if not request.key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Key is required."
        )

    created = WhiteboardService.set_content_by_key(request.key, request.content)

    if not created:
        return UpdateResponse(
            data=UpdateResponseData(
                flag=False,
                log="Failed to update whiteboard content."
            )
        )

    return UpdateResponse(
        data=UpdateResponseData(
            flag=True,
            log="Whiteboard content updated successfully.",
            created=created
        )
    )
