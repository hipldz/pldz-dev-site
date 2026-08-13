import hashlib
import os
import re
import threading
import time
from pathlib import Path

from PIL import Image, ImageOps, ImageSequence

from core import ProjectConfig


class ImageCacheStore:
    """Generate and atomically publish derived image variants."""

    @staticmethod
    def variant_path(
        source_path: str,
        category: str,
        image_name: str,
        width: int,
        height: int,
        quality: int,
        output_format: str,
    ) -> Path:
        cache_dir = Path(ProjectConfig.get_webp_cache_path())
        cache_dir.mkdir(parents=True, exist_ok=True)
        source_stat = Path(source_path).stat()
        image_key = f"{category}/{image_name}:{source_stat.st_mtime_ns}:{source_stat.st_size}"
        digest = hashlib.sha256(image_key.encode("utf-8")).hexdigest()[:12]
        safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(image_name).stem).strip("._") or "image"
        return cache_dir / f"{safe_stem}_{digest}_{width}x{height}_q{quality}.{output_format}"

    @staticmethod
    def inspect_source(source_path: str, selected_format: str) -> tuple[str, bool]:
        with Image.open(source_path) as source:
            is_animated = bool(getattr(source, "is_animated", False))
        return ("webp" if is_animated else selected_format), is_animated

    @staticmethod
    def _resize_keep_ratio(image: Image.Image, width: int, height: int) -> Image.Image:
        frame = ImageOps.exif_transpose(image)
        return ImageOps.contain(frame, (width, height), Image.Resampling.LANCZOS)

    @classmethod
    def _jpeg_ready(cls, image: Image.Image) -> Image.Image:
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.getchannel("A"))
            return background
        return image.convert("RGB")

    @classmethod
    def _save_static(
        cls, source: Image.Image, target: Path, width: int, height: int, quality: int, output_format: str
    ) -> None:
        resized = cls._resize_keep_ratio(source, width, height)
        if output_format == "jpeg":
            cls._jpeg_ready(resized).save(
                target, format="JPEG", quality=quality, optimize=True, progressive=True
            )
            return
        resized.save(
            target,
            format="WEBP",
            quality=quality,
            method=ProjectConfig.get_settings().webp_method,
        )

    @classmethod
    def _save_animated(
        cls, source: Image.Image, target: Path, width: int, height: int, quality: int
    ) -> None:
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(source):
            durations.append(frame.info.get("duration", source.info.get("duration", 100)))
            frames.append(cls._resize_keep_ratio(frame.convert("RGBA"), width, height))
        if not frames:
            raise ValueError("Invalid animated image")
        frames[0].save(
            target,
            format="WEBP",
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=source.info.get("loop", 0),
            quality=quality,
            method=ProjectConfig.get_settings().webp_method,
        )

    @classmethod
    def generate(
        cls,
        source_path: str,
        cache_path: Path,
        width: int,
        height: int,
        quality: int,
        output_format: str,
        is_animated: bool,
    ) -> None:
        if cache_path.exists():
            return
        temporary_path = cache_path.with_name(
            f".{cache_path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
        )
        try:
            with Image.open(source_path) as source:
                if is_animated:
                    cls._save_animated(source, temporary_path, width, height, quality)
                else:
                    cls._save_static(source, temporary_path, width, height, quality, output_format)
            os.replace(temporary_path, cache_path)
        finally:
            temporary_path.unlink(missing_ok=True)

    @staticmethod
    def cleanup(
        *,
        max_age_seconds: int = 30 * 24 * 60 * 60,
        max_bytes: int = 512 * 1024 * 1024,
    ) -> tuple[int, int]:
        """Remove stale variants and enforce a bounded image-cache size."""
        cache_dir = Path(ProjectConfig.get_webp_cache_path())
        if not cache_dir.is_dir():
            return 0, 0

        now = time.time()
        candidates = [
            path
            for path in cache_dir.iterdir()
            if path.is_file() and path.suffix.lower() in {".webp", ".jpeg", ".tmp"}
        ]
        removed_count = 0
        removed_bytes = 0

        for path in list(candidates):
            stat = path.stat()
            expiry = 60 * 60 if path.suffix.lower() == ".tmp" else max_age_seconds
            if now - stat.st_mtime <= expiry:
                continue
            path.unlink(missing_ok=True)
            removed_count += 1
            removed_bytes += stat.st_size
            candidates.remove(path)

        remaining = sorted(
            ((path.stat().st_mtime, path.stat().st_size, path) for path in candidates if path.exists()),
            key=lambda item: item[0],
        )
        total_bytes = sum(size for _, size, _ in remaining)
        for _, size, path in remaining:
            if total_bytes <= max_bytes:
                break
            path.unlink(missing_ok=True)
            total_bytes -= size
            removed_count += 1
            removed_bytes += size
        return removed_count, removed_bytes
