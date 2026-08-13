import os
from html import escape

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse

from core import Logger, ProjectConfig
from routes.path_utils import resolve_safe_file_path


WEBSITE_RESOURCE_ROUTER = APIRouter()


def _html_page(content: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>爬楼的猪 Dev 条款</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; line-height: 1.6; }}
            pre {{ white-space: pre-wrap; }}
        </style>
    </head>
    <body><pre>{content}</pre></body>
    </html>
    """


def _legal_response(filename: str, display_name: str) -> HTMLResponse:
    file_path = ProjectConfig.get_website_legal_path(filename)
    if not os.path.isfile(file_path):
        Logger.error(f"{display_name}文件未找到: {file_path}")
        return HTMLResponse(content=_html_page(f"{display_name}文件未找到"), status_code=404)

    with open(file_path, "r", encoding="utf-8") as file_obj:
        content = file_obj.read()
    if not content:
        Logger.error(f"{display_name}文件内容为空: {file_path}")
        return HTMLResponse(content=_html_page(f"{display_name}文件内容为空"), status_code=404)
    return HTMLResponse(content=_html_page(escape(content)), status_code=200)


@WEBSITE_RESOURCE_ROUTER.get("/website/legal/privacy-policy")
async def get_privacy_policy():
    """Return the Website privacy policy."""
    return _legal_response("privacy_policy.txt", "隐私政策")


@WEBSITE_RESOURCE_ROUTER.get("/website/legal/user-agreement")
async def get_user_agreement():
    """Return the Website user agreement."""
    return _legal_response("user_agreement.txt", "用户协议")


@WEBSITE_RESOURCE_ROUTER.get("/raw/{file_path:path}")
async def get_raw_resource(file_path: str):
    """Return a public resource file, never a DB file."""
    normalized_path, target_path = resolve_safe_file_path(
        ProjectConfig.get_resource_path(), file_path, "File path must be provided."
    )
    if not os.path.isfile(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource file '{normalized_path}' not found.",
        )
    return FileResponse(target_path)
