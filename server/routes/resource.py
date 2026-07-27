import os
import secrets
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, File, Header, Request, UploadFile, Depends, status
from fastapi.responses import HTMLResponse, FileResponse

from core import ProjectConfig, Logger
from scripts.filesystem import CacheCrudHandle
from scripts.filesystem.cache.cache_crud import MAX_CACHE_FILE_BYTES
from scripts.db import AuthorizedHandler
from .dependencies import ensure_admin_user
from .path_utils import resolve_safe_file_path


RESOURCE_ROUTE = APIRouter(prefix="/resource", tags=["resource"])


def _ensure_cache_admin(user: dict, action: str) -> None:
    ensure_admin_user(
        user,
        login_detail=f"You must be logged in to {action} cache files.",
        forbidden_detail=f"You do not have permission to {action} cache files.",
    )


def get_html_template(html_content: str) -> str:
    """
    获取 HTML 模板内容
    :param html_content: 要显示的 HTML 内容
    :return: 完整的 HTML 模板字符串
    """
    html = f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <title>爬楼的猪 Dev 条款</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; line-height: 1.6; }}
            pre {{ white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <pre>{html_content}</pre>
    </body>
    </html>
    """
    return html


@RESOURCE_ROUTE.get('/privacy_policy')
async def api_get_privacy_policy():
    """
    获取隐私政策
    :return: 隐私政策内容
    """
    # HTML 模板内容

    resource_path = ProjectConfig.get_resource_path()
    file_path = os.path.join(resource_path, 'privacy_policy.txt')
    if not os.path.exists(file_path):
        Logger.error(f"隐私政策文件未找到: {file_path}")
        html_response = get_html_template("隐私政策文件未找到")
        return HTMLResponse(content=html_response, status_code=404)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content:
        Logger.error(f"隐私政策文件内容为空: {file_path}")
        html_response = get_html_template("隐私政策文件内容为空")
        return HTMLResponse(content=html_response, status_code=404)

    # 将内容转换为 HTML 格式
    html_content = content.replace("\n", "<br>")
    html_response = get_html_template(html_content)

    return HTMLResponse(content=html_response, status_code=200)


@RESOURCE_ROUTE.get('/user_agreement')
async def api_get_user_agreement():
    """
    获取用户协议
    :return: 用户协议内容
    """
    # HTML 模板内容

    resource_path = ProjectConfig.get_resource_path()
    file_path = os.path.join(resource_path, 'user_agreement.txt')
    if not os.path.exists(file_path):
        Logger.error(f"用户协议文件未找到: {file_path}")
        html_response = get_html_template("用户协议文件未找到")
        return HTMLResponse(content=html_response, status_code=404)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content:
        Logger.error(f"用户协议文件内容为空: {file_path}")
        html_response = get_html_template("用户协议文件内容为空")
        return HTMLResponse(content=html_response, status_code=404)

    # 将内容转换为 HTML 格式
    html_content = content.replace("\n", "<br>")
    html_response = get_html_template(html_content)

    return HTMLResponse(content=html_response, status_code=200)


@RESOURCE_ROUTE.get('/raw/{file_path:path}')
async def api_get_raw_resource_file(file_path: str):
    """
    获取资源目录下的原始文件内容
    :param file_path: 相对于资源目录的文件路径
    :return: 原始文件响应
    """
    normalized_file_path, target_path = resolve_safe_file_path(
        ProjectConfig.get_resource_path(),
        file_path,
        "File path must be provided.",
    )

    if not os.path.isfile(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource file '{normalized_file_path}' not found."
        )

    return FileResponse(target_path)


@RESOURCE_ROUTE.get('/cache/all')
async def api_get_all_cache_files(user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    获取所有缓存文件
    :param user: 当前用户信息
    :return: 缓存文件列表
    """
    _ensure_cache_admin(user, "access")

    cache_files = CacheCrudHandle.get_all_cache_files()
    return {"data": cache_files}


class CacheDataRequest(BaseModel):
    filename: str


def _cache_file_response(filename: str) -> FileResponse:
    file_path = CacheCrudHandle.get_cache_file(filename)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cache file '{filename}' not found.",
        )
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)


def _parse_content_length(request: Request) -> int:
    try:
        content_length = int(request.headers.get("content-length", ""))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_411_LENGTH_REQUIRED, detail="Content-Length is required.") from error
    if content_length < 0:
        raise HTTPException(status_code=status.HTTP_411_LENGTH_REQUIRED, detail="Content-Length is required.")
    if content_length > MAX_CACHE_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Cache file exceeds the {MAX_CACHE_FILE_BYTES // 1024 // 1024} MB limit.",
        )
    return content_length


def _check_cache_token(cache_token: str) -> None:
    expected = os.environ.get("CACHE_API_TOKEN", "").strip()
    if not expected or not secrets.compare_digest(cache_token.strip(), expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid cache API token.",
        )


@RESOURCE_ROUTE.post('/cache/download')
async def api_download_cache_file(request: CacheDataRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    下载指定的缓存文件
    :param request: 请求体，包含要下载的文件名
    :param request.filename: 要下载的缓存文件名
    :param user: 当前用户信息
    :return: 缓存文件内容
    """
    _ensure_cache_admin(user, "download")

    filename = request.filename.strip()
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename must be provided."
        )

    return _cache_file_response(filename)


@RESOURCE_ROUTE.get('/cache/files/{filename}')
async def api_get_cache_file(
    filename: str,
    x_cache_token: str = Header("", alias="X-Cache-Token"),
):
    """使用机器令牌流式下载指定缓存文件。"""
    _check_cache_token(x_cache_token)
    return _cache_file_response(filename)


@RESOURCE_ROUTE.put('/cache/files/{filename}')
async def api_put_cache_file(
    filename: str,
    request: Request,
    x_cache_token: str = Header("", alias="X-Cache-Token"),
):
    """使用机器令牌以原始请求体流式上传缓存文件。"""
    _check_cache_token(x_cache_token)
    content_length = _parse_content_length(request)
    try:
        written = await CacheCrudHandle.save_cache_stream(
            filename, request.stream(), content_length=content_length
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except OSError as error:
        Logger.error(f"上传缓存文件失败: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save cache file.") from error
    return {"data": {"filename": filename, "bytes": written}}


@RESOURCE_ROUTE.get('/cache/raw/{filename:path}')
async def api_get_raw_cache_file(filename: str):
    """
    获取缓存目录下的原始文件内容
    :param filename: 缓存文件名
    :return: 原始文件响应
    """
    normalized_filename, target_path = resolve_safe_file_path(
        ProjectConfig.get_cache_path(),
        filename,
        "Filename must be provided.",
    )

    if not os.path.isfile(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cache file '{normalized_filename}' not found."
        )

    return FileResponse(target_path)


@RESOURCE_ROUTE.post('/cache/delete')
async def api_delete_cache_file(request: CacheDataRequest, user: dict = Depends(AuthorizedHandler.get_current_user)):
    """
    删除指定的缓存文件
    :param request: 请求体，包含要删除的文件名
    :param request.filename: 要删除的缓存文件名
    :param user: 当前用户信息
    :return: 删除结果
    """
    _ensure_cache_admin(user, "delete")

    filename = request.filename.strip()
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename must be provided."
        )

    success = CacheCrudHandle.delete_cache_file(filename)
    return {"data": success}


@RESOURCE_ROUTE.post('/cache/upload')
async def api_upload_cache_file(
    file: UploadFile = File(...),
    user: dict = Depends(AuthorizedHandler.get_current_user)
):
    """
    上传缓存文件
    :param file: 要上传的文件
    :param user: 当前用户信息
    :return: 上传结果
    """
    _ensure_cache_admin(user, "upload")

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename must be provided."
        )

    async def upload_chunks():
        while chunk := await file.read(1024 * 1024):
            yield chunk

    try:
        await CacheCrudHandle.save_cache_stream(file.filename, upload_chunks())
        return {"data": True}
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except OSError as error:
        Logger.error(f"上传缓存文件失败: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save cache file.") from error
