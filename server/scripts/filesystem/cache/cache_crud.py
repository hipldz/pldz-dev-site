"""Safe, atomic CRUD operations for files in the cache directory."""

from __future__ import annotations

import os
import tempfile
from collections.abc import AsyncIterable
from pathlib import Path

from core import Logger, ProjectConfig


CACHE_PATH = Path(ProjectConfig.get_cache_path())
MAX_CACHE_FILE_BYTES = 100 * 1024 * 1024


class CacheCrudHandle:
    """缓存文件的增删改查处理类。"""

    @classmethod
    def _cache_dir(cls) -> Path:
        CACHE_PATH.mkdir(parents=True, exist_ok=True)
        return CACHE_PATH

    @classmethod
    def _resolve_filename(cls, filename: str) -> Path:
        normalized_filename = filename.strip()
        if (
            not normalized_filename
            or normalized_filename in {".", ".."}
            or ".." in normalized_filename
            or "/" in normalized_filename
            or "\\" in normalized_filename
            or "\x00" in normalized_filename
        ):
            raise ValueError("Filename must be a plain cache file name.")
        return cls._cache_dir() / normalized_filename

    @classmethod
    def get_all_cache_files(cls) -> list[dict[str, str | float | int]]:
        """获取所有缓存文件的文件名、修改时间和大小。"""
        return [
            {
                "filename": file_path.name,
                "modified_time": file_path.stat().st_mtime,
                "size": file_path.stat().st_size,
            }
            for file_path in cls._cache_dir().iterdir()
            if file_path.is_file()
        ]

    @classmethod
    def get_cache_file(cls, filename: str) -> str:
        """获取指定缓存文件的绝对路径；文件不存在时返回空字符串。"""
        try:
            file_path = cls._resolve_filename(filename)
        except ValueError as error:
            Logger.error(f"非法缓存文件名 {filename!r}: {error}")
            return ""

        if file_path.is_file():
            return str(file_path)

        Logger.error(f"缓存文件 {filename} 不存在")
        return ""

    @classmethod
    def delete_cache_file(cls, filename: str) -> bool:
        """删除指定缓存文件。"""
        try:
            file_path = cls._resolve_filename(filename)
        except ValueError as error:
            Logger.error(f"非法缓存文件名 {filename!r}: {error}")
            return False

        if not file_path.is_file():
            Logger.error(f"缓存文件 {filename} 不存在")
            return False

        try:
            file_path.unlink()
            Logger.info(f"成功删除缓存文件: {filename}")
            return True
        except OSError as error:
            Logger.error(f"删除缓存文件失败: {error}")
            return False

    @classmethod
    def save_cache_file(cls, filename: str, data: bytes) -> bool:
        """保存小型缓存文件；大文件上传应使用 ``save_cache_stream``。"""
        if len(data) > MAX_CACHE_FILE_BYTES:
            Logger.error(f"缓存文件超过大小限制: {filename}")
            return False

        # 保留原同步 API 的兼容性；HTTP 上传走下方的流式 API。
        try:
            file_path = cls._resolve_filename(filename)
            cls._write_bytes_atomically(file_path, data)
            Logger.info(f"成功保存缓存文件: {filename}")
            return True
        except (OSError, ValueError) as error:
            Logger.error(f"保存缓存文件失败: {error}")
            return False

    @classmethod
    def _write_bytes_atomically(cls, file_path: Path, data: bytes) -> None:
        temporary_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix="cache-", suffix=".tmp", dir=file_path.parent, delete=False
            ) as target:
                temporary_file = Path(target.name)
                target.write(data)
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary_file, file_path)
        except Exception:
            if temporary_file:
                temporary_file.unlink(missing_ok=True)
            raise

    @classmethod
    async def save_cache_stream(
        cls,
        filename: str,
        chunks: AsyncIterable[bytes],
        *,
        content_length: int | None = None,
        max_bytes: int = MAX_CACHE_FILE_BYTES,
    ) -> int:
        """流式、原子地保存缓存文件，并返回实际写入字节数。"""
        if content_length is not None and (content_length < 0 or content_length > max_bytes):
            raise ValueError(f"Cache file exceeds the {max_bytes // 1024 // 1024} MB limit.")

        file_path = cls._resolve_filename(filename)
        temporary_file = None
        written = 0
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix="cache-", suffix=".tmp", dir=file_path.parent, delete=False
            ) as target:
                temporary_file = Path(target.name)
                async for chunk in chunks:
                    written += len(chunk)
                    if written > max_bytes:
                        raise ValueError(f"Cache file exceeds the {max_bytes // 1024 // 1024} MB limit.")
                    target.write(chunk)
                if content_length is not None and written != content_length:
                    raise ValueError("Upload ended before Content-Length bytes were received.")
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary_file, file_path)
        except Exception:
            if temporary_file:
                temporary_file.unlink(missing_ok=True)
            raise

        Logger.info(f"成功保存缓存文件: {filename} ({written} bytes)")
        return written


__all__ = ["CacheCrudHandle", "MAX_CACHE_FILE_BYTES"]
