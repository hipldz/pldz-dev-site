from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from services.website.comment import CommentService
from routes.dependencies import current_user, ensure_admin_user

COMMENTS_ROUTER = APIRouter(prefix="/website/comment", tags=["website-comments"])


class AllCommentsRequest(BaseModel):
    article_id: str


@COMMENTS_ROUTER.post("/all")
async def api_get_article_comments(request: AllCommentsRequest):
    """
    获取指定文章的所有评论
    :param article_id: 文章的唯一ID
    :return: 评论列表
    """
    article_id = request.article_id
    if not article_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article ID is required."
        )
    data = CommentService.get_all_comments_by_id(article_id)
    return {'data': data}


class AddCommentRequest(BaseModel):
    article_id: str
    content: dict
    parent_id: str


@COMMENTS_ROUTER.post("/add")
async def api_add_comment(request: AddCommentRequest, user: dict = Depends(current_user)):
    """
    添加评论
    """
    ensure_admin_user(
        user,
        login_detail="You must be logged in to add comments.",
        forbidden_detail="You do not have permission to sync articles.",
    )
    flag = CommentService.add_comment(request.article_id, request.content, request.parent_id)
    return {"data": flag}


class DeleteCommentRequest(BaseModel):
    article_id: str
    comment_id: str


@COMMENTS_ROUTER.post("/delete")
async def api_delete_comment(request: DeleteCommentRequest, user: dict = Depends(current_user)):
    """
    删除评论
    """
    ensure_admin_user(
        user,
        login_detail="You must be logged in to delete comments.",
        forbidden_detail="You do not have permission to delete comments.",
    )

    flag = CommentService.delete_comment(request.article_id, request.comment_id)
    return {"data": flag}
