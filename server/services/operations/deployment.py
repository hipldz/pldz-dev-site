import os
import platform
import re
import shutil
import tarfile
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener, url2pathname

from core import ProjectConfig
from storage.db.operations.deployment import DeploymentRecordStore
from storage.db.json_store import _lock as json_db_lock


DEPLOY_DB_FILENAME = "www_deployments.json"
GITHUB_API_VERSION = "2022-11-28"
MAX_LOG_LINES = 80
DEFAULT_MAX_ARTIFACT_BYTES = 100 * 1024 * 1024


class DeploymentService:
    _lock = json_db_lock

    @classmethod
    def create_record(cls, payload: dict) -> dict:
        now = cls._now()
        record = {
            "id": uuid.uuid4().hex,
            "folder": str(payload["folder"]).strip(),
            "artifact_url": str(payload["artifact_url"]).strip(),
            "artifact_path": "",
            "status": "queued",
            "started_at": "",
            "finished_at": "",
            "error": "",
            "log_tail": [],
            "created_at": now,
        }
        cls._append_record(record)
        return record

    @classmethod
    def list_records(cls) -> list[dict]:
        records = cls._read_records()
        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)

    @classmethod
    def retry_record(cls, record_id: str) -> dict | None:
        source = cls.get_record(record_id)
        if not source:
            return None

        return cls.create_record({
            "folder": source["folder"],
            "artifact_url": source["artifact_url"],
        })

    @classmethod
    def get_artifact_path(cls, record_id: str) -> Path:
        return Path(ProjectConfig.get_cache_path()) / "deployments" / "artifacts" / record_id / "artifact.zip"

    @classmethod
    def get_record(cls, record_id: str) -> dict | None:
        for record in cls._read_records():
            if record.get("id") == record_id:
                return record
        return None

    @classmethod
    def run_deploy(cls, record_id: str) -> None:
        logger = _DeployLog()
        cls._update_record(record_id, {"status": "running", "started_at": cls._now(), "error": "", "log_tail": []})

        work_dir = None
        backup_path = None
        target_path = None
        try:
            record = cls.get_record(record_id)
            if not record:
                raise RuntimeError("Deployment record not found.")

            folder = record["folder"]
            cls._validate_folder(folder)
            logger.add(f"Deploying artifact to www folder {folder}.")

            cache_root = Path(ProjectConfig.get_cache_path()) / "deployments" / "work" / record_id
            work_dir = cache_root
            archive_path = cls.get_artifact_path(record_id)
            extract_path = cache_root / "extract"
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            cache_root.mkdir(parents=True, exist_ok=True)

            cls._download_artifact(record["artifact_url"], archive_path, logger)
            cls._update_record(record_id, {"artifact_path": str(archive_path)})

            source_path = cls._extract_artifact(archive_path, extract_path, logger)
            cls._ensure_index_html(source_path)
            logger.add(f"Validated static site root {source_path}.")

            www_root = Path(ProjectConfig.get_www_path())
            backups_root = www_root / ".backups"
            www_root.mkdir(parents=True, exist_ok=True)
            backups_root.mkdir(parents=True, exist_ok=True)
            target_path = www_root / folder
            backup_path = backups_root / cls._backup_name(record, folder)

            cls._replace_target(source_path, target_path, backup_path, logger)
            cls._apply_permissions(target_path, logger)
            cls._update_record(record_id, {
                "status": "success",
                "finished_at": cls._now(),
                "error": "",
                "log_tail": logger.tail(),
            })
        except Exception as exc:
            logger.add(f"ERROR: {exc}")
            if target_path and backup_path and backup_path.exists() and not target_path.exists():
                try:
                    shutil.move(str(backup_path), str(target_path))
                    logger.add("Restored previous www folder after failure.")
                except Exception as restore_exc:
                    logger.add(f"ERROR: Failed to restore backup: {restore_exc}")
            cls._update_record(record_id, {
                "status": "failed",
                "finished_at": cls._now(),
                "error": str(exc),
                "log_tail": logger.tail(),
            })
        finally:
            if work_dir:
                shutil.rmtree(work_dir, ignore_errors=True)

    @classmethod
    def _validate_folder(cls, folder: str) -> None:
        if not folder or "/" in folder or "\\" in folder or ".." in folder:
            raise RuntimeError("WWW folder is not a safe folder name.")

    @classmethod
    def _download_artifact(cls, url: str, output_path: Path, logger) -> None:
        parsed = urlparse(url)
        if parsed.scheme == "file":
            source = Path(url2pathname(parsed.path))
            if not source.is_file():
                raise RuntimeError("Local artifact file does not exist.")
            shutil.copyfile(source, output_path)
            logger.add(f"Copied local artifact from {source}.")
        else:
            request = cls._build_github_artifact_request(url)
            opener = build_opener(_StripAuthRedirectHandler())
            logger.add(f"Downloading GitHub artifact from {request.full_url}.")
            try:
                with opener.open(request, timeout=300) as response:
                    cls._stream_response(response, output_path)
            except HTTPError as exc:
                raise RuntimeError(f"GitHub artifact download failed with HTTP {exc.code}: {cls._read_error(exc)}") from exc
            except URLError as exc:
                raise RuntimeError(f"GitHub artifact download failed: {exc.reason}") from exc

        if not output_path.exists() or output_path.stat().st_size <= 0:
            raise RuntimeError("Downloaded artifact is empty.")
        if output_path.stat().st_size > cls._max_artifact_bytes():
            raise RuntimeError("Downloaded artifact is too large.")
        if not zipfile.is_zipfile(output_path) and not tarfile.is_tarfile(output_path):
            raise RuntimeError("Downloaded artifact must be a zip or tar archive.")
        logger.add(f"Downloaded artifact size: {output_path.stat().st_size} bytes.")

    @classmethod
    def _build_github_artifact_request(cls, page_url: str) -> Request:
        owner, repo, artifact_id = cls._parse_github_artifact_url(page_url)
        token = os.environ.get("DEPLOY_GITHUB_TOKEN", "").strip()
        if not token:
            raise RuntimeError("DEPLOY_GITHUB_TOKEN must be configured on the server.")

        api_url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip"
        return Request(
            api_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": GITHUB_API_VERSION,
                "User-Agent": "pldz-dev-site-www-deployer",
            },
        )

    @classmethod
    def _parse_github_artifact_url(cls, page_url: str) -> tuple[str, str, str]:
        match = re.match(
            r"^https://github\.com/"
            r"(?P<owner>[^/]+)/"
            r"(?P<repo>[^/]+)/"
            r"actions/runs/\d+/artifacts/"
            r"(?P<artifact_id>\d+)/?"
            r"(?:\?.*)?$",
            page_url.strip(),
        )
        if not match:
            raise RuntimeError("Artifact URL must be a GitHub Actions artifact page URL.")
        return match.group("owner"), match.group("repo"), match.group("artifact_id")

    @classmethod
    def _stream_response(cls, response, output_path: Path) -> None:
        max_bytes = cls._max_artifact_bytes()
        downloaded = 0
        with open(output_path, "wb") as file_obj:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > max_bytes:
                    raise RuntimeError("Downloaded artifact is too large.")
                file_obj.write(chunk)

    @classmethod
    def _read_error(cls, exc: HTTPError) -> str:
        try:
            return exc.read(500).decode("utf-8", errors="replace").strip()
        except Exception:
            return str(exc)

    @classmethod
    def _max_artifact_bytes(cls) -> int:
        raw_value = os.environ.get("DEPLOY_MAX_ARTIFACT_BYTES", "").strip()
        if not raw_value:
            return DEFAULT_MAX_ARTIFACT_BYTES
        try:
            return max(1, int(raw_value))
        except ValueError:
            return DEFAULT_MAX_ARTIFACT_BYTES

    @classmethod
    def _extract_artifact(cls, archive_path: Path, extract_path: Path, logger) -> Path:
        extract_path.mkdir(parents=True, exist_ok=True)
        cls._extract_archive_to(archive_path, extract_path)
        logger.add("Extracted artifact.")

        nested_archive = cls._single_nested_archive(extract_path)
        if nested_archive:
            # Some workflows upload a pre-zipped dist file. GitHub then wraps
            # that file in the artifact zip, so the downloaded artifact has two
            # archive layers. Prefer uploading the dist directory, keep this as
            # a small tolerance for the double-archive shape.
            nested_extract_path = extract_path / "__nested_artifact__"
            nested_extract_path.mkdir(parents=True, exist_ok=True)
            cls._extract_archive_to(nested_archive, nested_extract_path)
            logger.add(f"Extracted nested artifact archive {nested_archive.name}.")
            return cls._select_site_root(nested_extract_path)

        return cls._select_site_root(extract_path)

    @classmethod
    def _extract_archive_to(cls, archive_path: Path, extract_path: Path) -> None:
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path) as archive:
                cls._validate_zip_members(archive)
                archive.extractall(extract_path)
            return
        if tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path) as archive:
                cls._validate_tar_members(archive)
                archive.extractall(extract_path)
            return
        raise RuntimeError("Artifact must be a zip or tar archive.")

    @classmethod
    def _single_nested_archive(cls, extract_path: Path) -> Path | None:
        visible_items = [item for item in extract_path.iterdir() if item.name != "__MACOSX"]
        if len(visible_items) != 1 or not visible_items[0].is_file():
            return None

        candidate = visible_items[0]
        if zipfile.is_zipfile(candidate) or tarfile.is_tarfile(candidate):
            return candidate
        return None

    @classmethod
    def _validate_zip_members(cls, archive: zipfile.ZipFile) -> None:
        for info in archive.infolist():
            cls._validate_archive_name(info.filename)
            mode = (info.external_attr >> 16) & 0o170000
            if mode in (0o120000, 0o10000):
                raise RuntimeError("Archive contains unsupported link entries.")

    @classmethod
    def _validate_tar_members(cls, archive: tarfile.TarFile) -> None:
        for member in archive.getmembers():
            cls._validate_archive_name(member.name)
            if member.issym() or member.islnk():
                raise RuntimeError("Archive contains unsupported link entries.")

    @classmethod
    def _validate_archive_name(cls, name: str) -> None:
        normalized_name = name.replace("\\", "/")
        target = Path(normalized_name)
        if target.is_absolute() or ".." in target.parts:
            raise RuntimeError("Archive contains an unsafe path.")
        if target.parts and ":" in target.parts[0]:
            raise RuntimeError("Archive contains an unsafe path.")

    @classmethod
    def _select_site_root(cls, extract_path: Path) -> Path:
        visible_items = [item for item in extract_path.iterdir() if item.name != "__MACOSX"]
        directories = [item for item in visible_items if item.is_dir()]
        files = [item for item in visible_items if item.is_file()]
        if len(directories) == 1 and not files:
            return directories[0]
        return extract_path

    @classmethod
    def _ensure_index_html(cls, source_path: Path) -> None:
        if not (source_path / "index.html").is_file():
            raise RuntimeError("Artifact does not contain index.html at the deployment root.")

    @classmethod
    def _replace_target(cls, source_path: Path, target_path: Path, backup_path: Path, logger) -> None:
        if target_path.exists():
            shutil.move(str(target_path), str(backup_path))
            logger.add(f"Backed up existing www folder to {backup_path}.")

        shutil.move(str(source_path), str(target_path))
        logger.add(f"Moved new www deployment into {target_path}.")

    @classmethod
    def _apply_permissions(cls, target_path: Path, logger) -> None:
        if platform.system().lower().startswith("win"):
            logger.add("Skipped chmod on Windows.")
            return

        for root, directories, files in os.walk(target_path):
            for dirname in directories:
                os.chmod(Path(root) / dirname, 0o755)
            for filename in files:
                os.chmod(Path(root) / filename, 0o644)
        os.chmod(target_path, 0o755)
        logger.add("Applied directory 755 and file 644 permissions.")

    @classmethod
    def _backup_name(cls, record: dict, folder: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{folder}-{timestamp}-{record['id'][:8]}"

    @classmethod
    def _append_record(cls, record: dict) -> None:
        with cls._lock:
            records = cls._read_records_unlocked()
            records.append(record)
            cls._write_records_unlocked(records)

    @classmethod
    def _update_record(cls, record_id: str, updates: dict) -> None:
        with cls._lock:
            records = cls._read_records_unlocked()
            for record in records:
                if record.get("id") == record_id:
                    record.update(updates)
                    break
            cls._write_records_unlocked(records)

    @classmethod
    def _read_records(cls) -> list[dict]:
        with cls._lock:
            return cls._read_records_unlocked()

    @classmethod
    def _read_records_unlocked(cls) -> list[dict]:
        return DeploymentRecordStore.read()

    @classmethod
    def _read_records_from_path(cls, db_path: Path) -> list[dict]:
        if not db_path.exists():
            return []
        from storage.db.json_store import _read_json
        payload = _read_json(str(db_path), default=[])
        return payload if isinstance(payload, list) else []

    @classmethod
    def _write_records_unlocked(cls, records: list[dict]) -> None:
        DeploymentRecordStore.write(records)

    @classmethod
    def _db_path(cls) -> Path:
        return Path(ProjectConfig.get_db_file_path("deployment", DEPLOY_DB_FILENAME))

    @classmethod
    def _now(cls) -> str:
        return datetime.now(timezone.utc).isoformat()


class _DeployLog:
    def __init__(self):
        self.lines = []

    def add(self, message: str) -> None:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.lines.append(f"{stamp} {message}")
        if len(self.lines) > MAX_LOG_LINES:
            self.lines = self.lines[-MAX_LOG_LINES:]

    def tail(self) -> list[str]:
        return list(self.lines[-MAX_LOG_LINES:])


class _StripAuthRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected:
            redirected.headers.pop("Authorization", None)
            redirected.unredirected_hdrs.pop("Authorization", None)
        return redirected
