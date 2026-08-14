import os
import secrets

from fastapi import APIRouter, Depends, File, Header, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core import Logger
from routes.dependencies import current_user, ensure_admin_user
from storage.cache.operations.files import MAX_CACHE_FILE_BYTES, CacheStore


CACHE_ROUTER = APIRouter(prefix="/cache", tags=["cache"])


class CacheDataRequest(BaseModel):
    filename: str


def _ensure_cache_admin(user: dict, action: str) -> None:
    ensure_admin_user(
        user,
        login_detail=f"You must be logged in to {action} cache files.",
        forbidden_detail=f"You do not have permission to {action} cache files.",
    )


def _cache_file_response(filename: str, *, download: bool = False) -> FileResponse:
    file_path = CacheStore.get_cache_file(filename)
    if not file_path:
        raise HTTPException(status_code=404, detail=f"Cache file '{filename}' not found.")
    return FileResponse(
        file_path,
        media_type="application/octet-stream" if download else None,
        filename=filename if download else None,
    )


def _parse_content_length(request: Request) -> int:
    try:
        content_length = int(request.headers.get("content-length", ""))
    except ValueError as error:
        raise HTTPException(status_code=411, detail="Content-Length is required.") from error
    if content_length < 0:
        raise HTTPException(status_code=411, detail="Content-Length is required.")
    if content_length > MAX_CACHE_FILE_BYTES:
        raise HTTPException(status_code=413, detail=f"Cache file exceeds the {MAX_CACHE_FILE_BYTES // 1024 // 1024} MB limit.")
    return content_length


def _check_cache_token(cache_token: str) -> None:
    expected = os.environ.get("CACHE_API_TOKEN", "").strip()
    if not expected or not secrets.compare_digest(cache_token.strip(), expected):
        raise HTTPException(status_code=403, detail="Invalid cache API token.")


@CACHE_ROUTER.get("/all")
async def get_all_cache_files(user: dict = Depends(current_user)):
    _ensure_cache_admin(user, "access")
    return {"data": CacheStore.get_all_cache_files()}


@CACHE_ROUTER.post("/download")
async def download_cache_file(payload: CacheDataRequest, user: dict = Depends(current_user)):
    _ensure_cache_admin(user, "download")
    if not payload.filename.strip():
        raise HTTPException(status_code=400, detail="Filename must be provided.")
    return _cache_file_response(payload.filename.strip(), download=True)


@CACHE_ROUTER.get("/files/{filename}")
async def get_cache_file(filename: str, x_cache_token: str = Header("", alias="X-Cache-Token")):
    _check_cache_token(x_cache_token)
    return _cache_file_response(filename)


@CACHE_ROUTER.put("/files/{filename}")
async def put_cache_file(
    filename: str,
    request: Request,
    x_cache_token: str = Header("", alias="X-Cache-Token"),
):
    _check_cache_token(x_cache_token)
    content_length = _parse_content_length(request)
    try:
        written = await CacheStore.save_cache_stream(filename, request.stream(), content_length=content_length)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except OSError as error:
        Logger.error(f"上传缓存文件失败: {error}")
        raise HTTPException(status_code=500, detail="Failed to save cache file.") from error
    return {"data": {"filename": filename, "bytes": written}}


@CACHE_ROUTER.post("/delete")
async def delete_cache_file(payload: CacheDataRequest, user: dict = Depends(current_user)):
    _ensure_cache_admin(user, "delete")
    if not payload.filename.strip():
        raise HTTPException(status_code=400, detail="Filename must be provided.")
    return {"data": CacheStore.delete_cache_file(payload.filename.strip())}


@CACHE_ROUTER.post("/upload")
async def upload_cache_file(file: UploadFile = File(...), user: dict = Depends(current_user)):
    _ensure_cache_admin(user, "upload")
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename must be provided.")

    async def upload_chunks():
        while chunk := await file.read(1024 * 1024):
            yield chunk

    try:
        await CacheStore.save_cache_stream(file.filename, upload_chunks())
        return {"data": True}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except OSError as error:
        Logger.error(f"上传缓存文件失败: {error}")
        raise HTTPException(status_code=500, detail="Failed to save cache file.") from error


@CACHE_ROUTER.get("/{file_path:path}")
async def get_public_cache_file(file_path: str):
    return _cache_file_response(file_path)
