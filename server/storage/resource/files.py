"""Read-only catalog for files published from the resource directory."""

from pathlib import Path

from core import ProjectConfig


class ResourceFileStore:
    @staticmethod
    def list_files() -> list[dict[str, str | float | int]]:
        root = Path(ProjectConfig.get_resource_path())
        if not root.is_dir():
            return []

        files = []
        for file_path in root.rglob("*"):
            if not file_path.is_file() or file_path.is_symlink():
                continue
            relative_path = file_path.relative_to(root).as_posix()
            parts = relative_path.split("/")
            stat = file_path.stat()
            files.append({
                "path": relative_path,
                "category": parts[0] if len(parts) > 1 else "",
                "filename": parts[-1],
                "modified_time": stat.st_mtime,
                "size": stat.st_size,
            })
        return sorted(files, key=lambda item: str(item["path"]).lower())


__all__ = ["ResourceFileStore"]
