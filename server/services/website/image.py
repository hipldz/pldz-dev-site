import asyncio
import io
import weakref
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

from core import Logger, ProjectConfig
from storage.cache.website.image import ImageCacheStore


MAX_IMAGE_SIZE = 2000
DEFAULT_IMAGE_WIDTH = 512
DEFAULT_IMAGE_HEIGHT = 512
DEFAULT_IMAGE_QUALITY = 80
SUPPORTED_OUTPUT_FORMATS = {"webp", "jpeg"}
SUPPORTED_UPLOAD_FORMATS = {"GIF", "JPEG", "PNG", "WEBP"}
MAX_IMAGE_UPLOAD_BYTES = 20 * 1024 * 1024


class ImageProcessingError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass(frozen=True)
class ImageVariant:
    path: Path
    media_type: str


class ImageService:
    _semaphore = asyncio.Semaphore(ProjectConfig.get_settings().image_process_concurrency)
    _cache_locks: weakref.WeakValueDictionary[Path, asyncio.Lock] = weakref.WeakValueDictionary()
    _cache_locks_guard = asyncio.Lock()

    @staticmethod
    def validate_dimensions(width: int, height: int) -> None:
        if width <= 0 or height <= 0 or width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
            raise ImageProcessingError(400, f"非法图片尺寸，宽高必须在 1-{MAX_IMAGE_SIZE} 之间")

    @staticmethod
    def validate_quality(quality: int) -> None:
        if quality < 1 or quality > 95:
            raise ImageProcessingError(400, "非法图片质量，quality 必须在 1-95 之间")

    @staticmethod
    def select_output_format(accept: str, output_format: str | None) -> str:
        if output_format:
            normalized = output_format.lower()
            if normalized not in SUPPORTED_OUTPUT_FORMATS:
                raise ImageProcessingError(400, "非法图片格式，仅支持 webp/jpeg")
            return normalized
        return "webp" if "image/webp" in accept or "*/*" in accept or not accept else "jpeg"

    @staticmethod
    def validate_upload(data: bytes) -> None:
        if not data:
            raise ImageProcessingError(400, "图片文件不能为空")
        if len(data) > MAX_IMAGE_UPLOAD_BYTES:
            raise ImageProcessingError(413, "图片文件不能超过 20 MB")
        try:
            with Image.open(io.BytesIO(data)) as source:
                if source.format not in SUPPORTED_UPLOAD_FORMATS:
                    raise ImageProcessingError(400, "仅支持 GIF/JPEG/PNG/WebP 图片")
                source.verify()
        except ImageProcessingError:
            raise
        except (UnidentifiedImageError, OSError) as error:
            raise ImageProcessingError(400, "无效的图片文件") from error

    @classmethod
    async def _get_cache_lock(cls, cache_path: Path) -> asyncio.Lock:
        async with cls._cache_locks_guard:
            lock = cls._cache_locks.get(cache_path)
            if lock is None:
                lock = asyncio.Lock()
                cls._cache_locks[cache_path] = lock
            return lock

    @classmethod
    async def build_variant(
        cls,
        source_path: str,
        category: str,
        image_name: str,
        width: int,
        height: int,
        quality: int,
        accept: str,
        output_format: str | None,
    ) -> ImageVariant:
        cls.validate_dimensions(width, height)
        cls.validate_quality(quality)
        selected_format = cls.select_output_format(accept, output_format)
        try:
            selected_format, is_animated = await run_in_threadpool(
                ImageCacheStore.inspect_source, source_path, selected_format
            )
            cache_path = ImageCacheStore.variant_path(
                source_path, category, image_name, width, height, quality, selected_format
            )
            if not cache_path.exists():
                cache_lock = await cls._get_cache_lock(cache_path)
                async with cache_lock:
                    if not cache_path.exists():
                        async with cls._semaphore:
                            await run_in_threadpool(
                                ImageCacheStore.generate,
                                source_path,
                                cache_path,
                                width,
                                height,
                                quality,
                                selected_format,
                                is_animated,
                            )
        except UnidentifiedImageError as error:
            raise ImageProcessingError(400, "无效的图片文件") from error
        except ImageProcessingError:
            raise
        except Exception as error:
            Logger.error(f"处理图片失败: {error}")
            raise ImageProcessingError(500, "内部服务器错误，图片处理失败") from error

        media_type = "image/jpeg" if selected_format == "jpeg" else "image/webp"
        return ImageVariant(cache_path, media_type)
