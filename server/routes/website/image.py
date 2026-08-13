import mimetypes
import re

from fastapi import (
    APIRouter,
    HTTPException,
    File,
    UploadFile,
    Form,
    Depends,
    Query,
    Request,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core import Logger
from services.website.image import (
    DEFAULT_IMAGE_HEIGHT,
    DEFAULT_IMAGE_QUALITY,
    DEFAULT_IMAGE_WIDTH,
    ImageProcessingError,
    ImageService,
    MAX_IMAGE_UPLOAD_BYTES,
)
from storage.resource.website.image import ImageResourceError, ImageResourceStore
from routes.dependencies import current_user, ensure_admin_user, ensure_authenticated
from routes.path_utils import has_invalid_path_part

IMAGES_ROUTER = APIRouter(prefix="/website/image", tags=["website-image"])

CACHE_CONTROL_HEADER = {"Cache-Control": "public, max-age=86400"}
ADMIN_REQUIRED_DETAIL = "You do not have permission to sync articles."
LOGIN_REQUIRED_DETAIL = "You must be logged in to sync articles."


def _ensure_image_admin(user: dict) -> None:
    ensure_admin_user(
        user,
        login_detail=LOGIN_REQUIRED_DETAIL,
        forbidden_detail=ADMIN_REQUIRED_DETAIL,
    )


def _image_store_call(method, *args):
    try:
        return method(*args)
    except ImageResourceError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


def _validate_image_request(category: str, image: str) -> None:
    if has_invalid_path_part(category):
        raise HTTPException(status_code=400, detail="非法的图片分类")
    if has_invalid_path_part(image):
        raise HTTPException(status_code=400, detail="非法的图片文件名")


def _parse_dimension(value: str) -> int:
    if not re.fullmatch(r"\d{1,4}", value):
        raise HTTPException(status_code=400, detail="非法图片尺寸格式，示例：128x128")
    return int(value)


def _parse_quality(quality: str) -> int:
    if not re.fullmatch(r"\d{1,2}", quality):
        raise HTTPException(status_code=400, detail="非法图片质量，quality 必须在 1-95 之间")
    quality_value = int(quality)
    try:
        ImageService.validate_quality(quality_value)
    except ImageProcessingError as error:
        raise HTTPException(error.status_code, error.detail) from error
    return quality_value


async def _read_validated_upload(file: UploadFile) -> bytes:
    data = await file.read(MAX_IMAGE_UPLOAD_BYTES + 1)
    try:
        ImageService.validate_upload(data)
    except ImageProcessingError as error:
        raise HTTPException(error.status_code, error.detail) from error
    return data


async def _build_image_response(
    category: str,
    image: str,
    width: int | None,
    height: int | None,
    request: Request,
    quality: str,
    output_format: str | None,
) -> FileResponse:
    _validate_image_request(category, image)
    quality_value = _parse_quality(quality)
    path = _image_store_call(ImageResourceStore.get_image_path, category, image)
    try:
        if width is None or height is None:
            width = DEFAULT_IMAGE_WIDTH
            height = DEFAULT_IMAGE_HEIGHT
        variant = await ImageService.build_variant(
            path,
            category,
            image,
            width,
            height,
            quality_value,
            request.headers.get("accept", ""),
            output_format,
        )
    except ImageProcessingError as error:
        raise HTTPException(error.status_code, error.detail) from error
    return FileResponse(variant.path, media_type=variant.media_type, headers=CACHE_CONTROL_HEADER)


def _build_original_image_response(category: str, image: str) -> FileResponse:
    _validate_image_request(category, image)
    path = _image_store_call(ImageResourceStore.get_image_path, category, image)
    media_type, _ = mimetypes.guess_type(path)
    return FileResponse(
        path,
        media_type=media_type or "application/octet-stream",
        headers=CACHE_CONTROL_HEADER,
    )


@IMAGES_ROUTER.get("/{category}/{image}@{width}x{height}")
async def api_get_resized_image(
    category: str,
    image: str,
    width: str,
    height: str,
    request: Request,
    quality: str = Query(str(DEFAULT_IMAGE_QUALITY)),
    format: str | None = Query(None),
):
    """
    获取指定分类下的压缩图片，按请求尺寸等比缩放并输出 WebP/JPEG。
    :param category: 图片分类
    :param image: 图片文件名
    :param width: 目标宽度
    :param height: 目标高度
    """
    return await _build_image_response(
        category,
        image,
        _parse_dimension(width),
        _parse_dimension(height),
        request,
        quality,
        format,
    )


@IMAGES_ROUTER.get("/{category}/{image}@original")
async def api_get_original_image(category: str, image: str):
    """
    获取指定分类下的原始图片文件，不进行缩放和格式转换。
    :param category: 图片分类
    :param image: 图片文件名
    """
    return _build_original_image_response(category, image)


@IMAGES_ROUTER.get("/{category}/{image}@{size}")
async def api_get_square_resized_image(
    category: str,
    image: str,
    size: str,
    request: Request,
    quality: str = Query(str(DEFAULT_IMAGE_QUALITY)),
    format: str | None = Query(None),
):
    """
    获取指定分类下的压缩图片，单个尺寸参数表示宽高相同。
    :param category: 图片分类
    :param image: 图片文件名
    :param size: 目标宽高
    """
    parsed_size = _parse_dimension(size)
    return await _build_image_response(
        category,
        image,
        parsed_size,
        parsed_size,
        request,
        quality,
        format,
    )


@IMAGES_ROUTER.get("/{category}/{image}")
async def api_get_image(
    category: str,
    image: str,
    request: Request,
    quality: str = Query(str(DEFAULT_IMAGE_QUALITY)),
    format: str | None = Query(None),
):
    """
    获取指定分类下的压缩图片
    :param category: 图片分类
    :param image: 图片文件名
    """
    return await _build_image_response(category, image, None, None, request, quality, format)


class ImageCategoryData(BaseModel):
    category: str


@IMAGES_ROUTER.post("/category/all")
async def api_post_all_images(category: ImageCategoryData, user: dict = Depends(current_user)):
    """
    获取指定分类下的所有图片
    :param category: 图片分类
    """
    _ensure_image_admin(user)

    try:
        images = _image_store_call(ImageResourceStore.get_all_images, category.category)
    except Exception as e:
        Logger.error(f"获取所有图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

    return {"data": images}


class ImageRenameData(BaseModel):
    category: str
    oldName: str
    newName: str


@IMAGES_ROUTER.post("/rename")
async def api_rename_image(
    payload: ImageRenameData,
    user: dict = Depends(current_user)
):
    """
    重命名指定分类下的图片
    :param payload: 包含分类和新旧图片名的请求体
    :param user: 当前用户
    """
    _ensure_image_admin(user)

    if has_invalid_path_part(payload.newName):
        raise HTTPException(400, "非法文件名")

    try:
        new_name = _image_store_call(ImageResourceStore.rename_image, payload.category, payload.oldName, payload.newName)
    except HTTPException:
        # 如果 handler 已经抛了 HTTPException，就直接 re-raise
        raise
    except Exception as e:
        Logger.error(f"重命名图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误，重命名失败")

    return {"data": {"flag": True, "new_name": new_name}}


class ImageData(BaseModel):
    category: str
    name: str


@IMAGES_ROUTER.post("/delete")
async def api_delete_image(
    payload: ImageData,
    user: dict = Depends(current_user)
):
    """
    删除指定分类下的图片
    :param payload: 包含分类和图片名的请求体
    :param user: 当前用户
    """
    _ensure_image_admin(user)

    try:
        success = _image_store_call(ImageResourceStore.delete_image, payload.category, payload.name)
        if not success:
            raise HTTPException(status_code=404, detail="图片未找到")
    except HTTPException:
        # 如果 handler 已经抛了 HTTPException，就直接 re-raise
        raise
    except Exception as e:
        Logger.error(f"删除图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误，删除失败")

    return {"data": {"flag": True}}


@IMAGES_ROUTER.post("/upload/avatar")
async def api_upload_avatar(
    file: UploadFile = File(...),
    name: str = Form(...),
    user: dict = Depends(current_user)
):
    """
    上传用户头像
    :param file: 上传的文件
    :param name: 文件名
    :param user: 当前用户
    """
    # 验证用户是否已登录

    ensure_authenticated(user, detail="未授权的用户", status_code=403)
    if has_invalid_path_part(name):
        raise HTTPException(400, "非法文件名")

    data = await _read_validated_upload(file)
    try:
        saved_name = _image_store_call(ImageResourceStore.save_avatar, data, file.filename, user.get("username", "unknown"))
    except HTTPException:
        # 如果 handler 已经抛了 HTTPException，就直接 re-raise
        raise
    except Exception as e:
        Logger.error(f"保存头像失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误，头像保存失败")

    url = f"/api/v1/website/image/avatar/{saved_name}"
    return {"data": {"flag": True, "url": url}}


@IMAGES_ROUTER.post("/upload/article")
async def api_upload_article_image(
    file: UploadFile = File(...),
    category: str = Form(...),
    name: str = Form(...),
    user: dict = Depends(current_user)
):
    """
    上传文章图片
    :param file: 上传的文件
    :param category: 图片分类
    :param name: 文件名
    :param user: 当前用户
    """
    # 验证用户是否已登录
    ensure_authenticated(user, detail="未授权的用户", status_code=403)
    if has_invalid_path_part(category) or has_invalid_path_part(name):
        raise HTTPException(400, "非法文件名")

    data = await _read_validated_upload(file)
    try:
        saved_name = _image_store_call(ImageResourceStore.save_article_image, data, category, name, file.filename)
    except Exception as e:
        Logger.error(f"保存文章图片失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误，图片保存失败")

    url = f"/api/v1/website/image/{category}/{saved_name}"
    return {"data": {"flag": True, "url": url}}


class ImageCheck(BaseModel):
    category: str
    name: str


@IMAGES_ROUTER.post("/upload/check")
async def api_check_image_exist(
    payload: ImageCheck,
    user: dict = Depends(current_user)
):
    """
    检查指定分类下的图片是否已存在
    :param payload: 包含分类和图片名的请求体
    :param user: 当前用户
    """
    # 验证用户是否已登录
    ensure_authenticated(user, detail="未授权的用户", status_code=403)
    exists = _image_store_call(ImageResourceStore.check_exists, payload.category, payload.name)
    return {"data": not exists}
