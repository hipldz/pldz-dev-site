import os
import hashlib
import tempfile
from pathlib import Path
from uuid import uuid4

from core import Logger, ProjectConfig


class ImageResourceError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class ImageResourceStore:
    @staticmethod
    def _safe_name(value: str, label: str) -> str:
        normalized = str(value or "").strip()
        if (
            not normalized
            or normalized in {".", ".."}
            or "/" in normalized
            or "\\" in normalized
            or "\x00" in normalized
        ):
            raise ImageResourceError(400, f"非法的{label}")
        return normalized

    @classmethod
    def _category_dir(cls, category: str, *, create: bool = False) -> Path:
        safe_category = cls._safe_name(category, "图片分类")
        base_dir = Path(ProjectConfig.get_images_path()).resolve()
        category_dir = (base_dir / safe_category).resolve()
        if category_dir.parent != base_dir:
            raise ImageResourceError(400, "非法的图片分类")
        if create:
            category_dir.mkdir(parents=True, exist_ok=True)
        return category_dir

    @staticmethod
    def _write_atomically(target: Path, bytes_data: bytes) -> None:
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=f".{target.stem}-", suffix=".tmp", dir=target.parent, delete=False
            ) as file_obj:
                temporary_path = Path(file_obj.name)
                file_obj.write(bytes_data)
                file_obj.flush()
                os.fsync(file_obj.fileno())
            os.replace(temporary_path, target)
        finally:
            if temporary_path:
                temporary_path.unlink(missing_ok=True)

    @staticmethod
    def get_image_path(category: str, filename: str) -> str:
        """
        获取指定分类下的图片绝对路径
        :param category: 图片分类
        :param filename: 图片文件名
        """
        category_dir = ImageResourceStore._category_dir(category)
        safe_filename = ImageResourceStore._safe_name(filename, "图片文件名")
        full_path = category_dir / safe_filename
        if not full_path.is_file():
            Logger.error(f"图片未找到: {full_path}")
            raise ImageResourceError(404, "图片未找到")
        return str(full_path)

    @classmethod
    def get_all_images(cls, category: str) -> list:
        """
        获取指定分类下的所有图片文件名
        :param category: 图片分类
        """
        category_dir = cls._category_dir(category)
        if not category_dir.exists():
            Logger.error(f"分类目录不存在: {category_dir}")
            raise ImageResourceError(404, "分类目录不存在")

        images = [p.name for p in category_dir.iterdir() if p.is_file()]
        return images

    @staticmethod
    def save_avatar(bytes_data: bytes, original_name: str, username: str) -> str:
        """
        保存用户头像到指定目录，并生成唯一文件名
        :param bytes_data: 头像的二进制数据
        :param original_name: 原始文件名
        :param username: 用户名，用于生成唯一文件名
        """
        suffix = Path(original_name).suffix.lower() or ".img"
        avatar_dir = ImageResourceStore._category_dir("avatar", create=True)
        user_key = hashlib.sha256(username.encode("utf-8")).hexdigest()[:16]
        unique_name = f"{user_key}_{uuid4().hex[:8]}{suffix}"
        target = avatar_dir / unique_name

        try:
            ImageResourceStore._write_atomically(target, bytes_data)
        except Exception as e:
            Logger.error(f"保存 avatar 失败: {e}")
            # 给出错误信息
            raise ImageResourceError(500, f"保存头像失败: {e}") from e
        return unique_name

    @staticmethod
    def save_article_image(bytes_data: bytes, category: str, name: str, original_name: str) -> str:
        """
        保存文章图片到指定分类目录，并生成唯一文件名
        :param bytes_data: 图片的二进制数据
        :param category: 图片分类
        :param name: 文件名（不含扩展名）
        :param original_name: 原始文件名
        """
        suffix = Path(original_name).suffix.lower() or ".img"
        category_dir = ImageResourceStore._category_dir(category, create=True)

        target_name = f"{ImageResourceStore._safe_name(name, '图片文件名')}{suffix}"
        target = category_dir / target_name
        try:
            ImageResourceStore._write_atomically(target, bytes_data)
        except Exception as e:
            Logger.error(f"保存文章图片失败: {e}")
            raise ImageResourceError(500, f"保存文章图片失败: {e}") from e
        return target_name

    @staticmethod
    def check_exists(category: str, stem: str) -> bool:
        """
        检查指定分类下是否已存在同名图片
        :param category: 图片分类
        :param stem: 图片文件名（不含扩展名）
        """
        category_dir = ImageResourceStore._category_dir(category, create=True)
        existing = {p.stem for p in category_dir.iterdir() if p.is_file()}
        return stem in existing

    @classmethod
    def rename_image(cls, category: str, old_name: str, new_name: str) -> str:
        """
        重命名指定分类下的图片
        :param category: 图片分类
        :param old_name: 原文件名
        :param new_name: 新文件名
        """
        category_dir = cls._category_dir(category)
        if not category_dir.exists():
            Logger.error(f"分类目录不存在: {category_dir}")
            raise ImageResourceError(404, "分类目录不存在")

        old_path = category_dir / cls._safe_name(old_name, "图片文件名")
        if not old_path.is_file():
            Logger.error(f"原图片未找到: {old_path}")
            raise ImageResourceError(404, "原图片未找到")

        new_name = cls._safe_name(new_name, "图片文件名")
        new_path = category_dir / new_name
        if new_path.exists():
            Logger.error(f"新图片名已存在: {new_path}")
            raise ImageResourceError(400, "新图片名已存在")

        try:
            old_path.rename(new_path)
        except Exception as e:
            Logger.error(f"重命名图片失败: {e}")
            raise ImageResourceError(500, f"重命名图片失败: {e}") from e

        return new_name

    @classmethod
    def delete_image(cls, category: str, filename: str) -> bool:
        """
        删除指定分类下的图片
        :param category: 图片分类
        :param filename: 图片文件名
        """
        category_dir = cls._category_dir(category)
        if not category_dir.exists():
            Logger.error(f"分类目录不存在: {category_dir}")
            raise ImageResourceError(404, "分类目录不存在")

        file_path = category_dir / cls._safe_name(filename, "图片文件名")
        if not file_path.is_file():
            Logger.error(f"图片未找到: {file_path}")
            raise ImageResourceError(404, "图片未找到")

        try:
            file_path.unlink()
        except Exception as e:
            Logger.error(f"删除图片失败: {e}")
            raise ImageResourceError(500, f"删除图片失败: {e}") from e

        return True
