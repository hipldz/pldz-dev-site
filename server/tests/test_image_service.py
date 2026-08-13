import os
import pytest
from pathlib import Path

from PIL import Image

from storage.cache.website.image import ImageCacheStore
from services.website.image import ImageProcessingError, ImageService
from storage.resource.website.image import ImageResourceError, ImageResourceStore


def test_image_cache_key_changes_when_source_is_replaced(tmp_path, monkeypatch):
    from core import ProjectConfig

    monkeypatch.setattr(ProjectConfig, "PROJECT_ROOT", str(tmp_path))
    source = tmp_path / "source.png"
    Image.new("RGB", (8, 8), "red").save(source)
    first = ImageCacheStore.variant_path(str(source), "test", "source.png", 8, 8, 80, "webp")

    Image.new("RGB", (9, 9), "blue").save(source)
    stat = source.stat()
    os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1))
    second = ImageCacheStore.variant_path(str(source), "test", "source.png", 8, 8, 80, "webp")

    assert first != second


def test_image_cache_cleanup_enforces_size_limit(tmp_path, monkeypatch):
    from core import ProjectConfig

    monkeypatch.setattr(ProjectConfig, "PROJECT_ROOT", str(tmp_path))
    cache_dir = tmp_path / "data" / "cache" / "webp"
    cache_dir.mkdir(parents=True)
    first = cache_dir / "first.webp"
    second = cache_dir / "second.webp"
    first.write_bytes(b"a" * 10)
    second.write_bytes(b"b" * 10)
    os.utime(first, (1, 1))

    removed_count, removed_bytes = ImageCacheStore.cleanup(
        max_age_seconds=10**12,
        max_bytes=10,
    )

    assert (removed_count, removed_bytes) == (1, 10)
    assert not first.exists()
    assert second.exists()


def test_image_upload_validation_rejects_non_images():
    with pytest.raises(ImageProcessingError, match="无效"):
        ImageService.validate_upload(b"not an image")


def test_image_resource_store_rejects_category_traversal(tmp_path, monkeypatch):
    from core import ProjectConfig

    monkeypatch.setattr(ProjectConfig, "PROJECT_ROOT", str(tmp_path))
    with pytest.raises(ImageResourceError, match="分类"):
        ImageResourceStore.save_article_image(b"data", "../outside", "name", "image.png")
