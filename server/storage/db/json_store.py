import os
import json
import copy
import tempfile
import threading
from pathlib import Path

from core import ProjectConfig

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows development fallback
    fcntl = None


class JsonProcessLock:
    """Serialize JSON DB read-modify-write transactions across processes."""

    def __init__(self):
        self._thread_lock = threading.RLock()
        self._local = threading.local()

    def __enter__(self):
        self._thread_lock.acquire()
        try:
            depth = getattr(self._local, "depth", 0)
            if depth == 0 and fcntl is not None:
                lock_path = Path(ProjectConfig.get_db_path()) / ".json-store.lock"
                lock_path.parent.mkdir(parents=True, exist_ok=True)
                lock_file = lock_path.open("a+")
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                self._local.lock_file = lock_file
            self._local.depth = depth + 1
            return self
        except Exception:
            self._thread_lock.release()
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        depth = self._local.depth - 1
        self._local.depth = depth
        if depth == 0:
            lock_file = getattr(self._local, "lock_file", None)
            if lock_file is not None:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                lock_file.close()
                del self._local.lock_file
        self._thread_lock.release()


_lock = JsonProcessLock()


class JsonStoreError(RuntimeError):
    """Raised when a JSON DB exists but cannot be read safely."""


def _read_json(filepath: str, *, default=None):
    if not os.path.exists(filepath):
        return copy.deepcopy({} if default is None else default)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as error:
        raise JsonStoreError(f"无法安全读取 JSON DB: {filepath}") from error


def _write_json(filepath: str, data) -> None:
    target = Path(filepath)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            prefix=f'{target.stem}-',
            suffix='.tmp',
            dir=target.parent,
            delete=False,
        ) as file_obj:
            temp_path = Path(file_obj.name)
            json.dump(data, file_obj, ensure_ascii=False, indent=2)
            file_obj.flush()
            os.fsync(file_obj.fileno())
        os.replace(temp_path, target)
        # Persist the directory entry as well as the file contents on POSIX.
        directory_fd = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


def get_article_views_db_path() -> str:
    return ProjectConfig.get_article_views_db_path()


def get_users_db_path() -> str:
    return ProjectConfig.get_db_file_path('identity', 'users.json')


def get_comments_db_path() -> str:
    return ProjectConfig.get_db_file_path('content', 'comments.json')


def get_analytics_db_path() -> str:
    return ProjectConfig.get_db_file_path('analytics', 'analytics.json')


def get_deployments_db_path() -> str:
    return ProjectConfig.get_db_file_path('deployment', 'www_deployments.json')
