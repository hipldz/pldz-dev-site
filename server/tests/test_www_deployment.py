import json
import zipfile
from pathlib import Path


def _write_zip(path: Path, files: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def _setup_project(monkeypatch, tmp_path: Path):
    from core import ProjectConfig

    monkeypatch.setattr(ProjectConfig, "PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("DEPLOY_NOTICE_TOKEN", "secret")
    (tmp_path / "data" / "db").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "cache").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "www").mkdir(parents=True, exist_ok=True)


def _notice_payload(artifact_url: str, folder: str = "demo") -> dict:
    return {
        "folder": folder,
        "artifact_url": artifact_url,
    }


def _headers(token: str = "secret") -> dict:
    return {"X-Deploy-Token": token}


def _records(tmp_path: Path) -> list[dict]:
    with open(tmp_path / "data" / "db" / "deployment" / "www_deployments.json", "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def test_www_deployment_notice_rejects_missing_or_wrong_token(client, monkeypatch, tmp_path):
    _setup_project(monkeypatch, tmp_path)
    zip_path = tmp_path / "site.zip"
    _write_zip(zip_path, {"index.html": "hello"})

    assert client.post(
        "/api/v1/deploy/www/notice",
        json=_notice_payload(zip_path.as_uri()),
    ).status_code == 403

    assert client.post(
        "/api/v1/deploy/www/notice",
        json=_notice_payload(zip_path.as_uri()),
        headers=_headers("bad"),
    ).status_code == 403


def test_www_deployment_success_replaces_target_and_creates_backup(client, monkeypatch, tmp_path):
    _setup_project(monkeypatch, tmp_path)
    target = tmp_path / "data" / "www" / "demo"
    target.mkdir(parents=True)
    (target / "index.html").write_text("old", encoding="utf-8")

    zip_path = tmp_path / "site.zip"
    _write_zip(zip_path, {"dist/index.html": "new", "dist/app.js": "console.log(1)"})

    response = client.post(
        "/api/v1/deploy/www/notice",
        json=_notice_payload(zip_path.as_uri()),
        headers=_headers(),
    )

    assert response.status_code == 200
    assert (target / "index.html").read_text(encoding="utf-8") == "new"
    assert (target / "app.js").is_file()
    backups = list((tmp_path / "data" / "www" / ".backups").glob("demo-*"))
    assert backups
    records = _records(tmp_path)
    assert records[-1]["status"] == "success"
    assert records[-1]["folder"] == "demo"


def test_www_deployment_allows_main_website_folder(client, monkeypatch, tmp_path):
    _setup_project(monkeypatch, tmp_path)
    target = tmp_path / "data" / "www" / "website"
    target.mkdir(parents=True)
    (target / "index.html").write_text("old", encoding="utf-8")

    zip_path = tmp_path / "site.zip"
    _write_zip(zip_path, {"index.html": "main", "assets/app.js": "console.log(1)"})

    response = client.post(
        "/api/v1/deploy/www/notice",
        json=_notice_payload(zip_path.as_uri(), folder="website"),
        headers=_headers(),
    )

    assert response.status_code == 200
    assert (target / "index.html").read_text(encoding="utf-8") == "main"
    assert (target / "assets" / "app.js").is_file()
    records = _records(tmp_path)
    assert records[-1]["status"] == "success"
    assert records[-1]["folder"] == "website"


def test_www_deployment_extracts_single_nested_archive(client, monkeypatch, tmp_path):
    _setup_project(monkeypatch, tmp_path)
    target = tmp_path / "data" / "www" / "demo"
    target.mkdir(parents=True)
    (target / "index.html").write_text("old", encoding="utf-8")

    inner_zip_path = tmp_path / "demo-dist.zip"
    outer_zip_path = tmp_path / "artifact.zip"
    _write_zip(inner_zip_path, {"dist/index.html": "nested", "dist/app.js": "console.log(2)"})

    with zipfile.ZipFile(outer_zip_path, "w") as archive:
        archive.write(inner_zip_path, "demo-dist.zip")

    response = client.post(
        "/api/v1/deploy/www/notice",
        json=_notice_payload(outer_zip_path.as_uri()),
        headers=_headers(),
    )

    assert response.status_code == 200
    assert (target / "index.html").read_text(encoding="utf-8") == "nested"
    assert (target / "app.js").is_file()
    records = _records(tmp_path)
    assert records[-1]["status"] == "success"
    assert any("nested artifact archive" in line for line in records[-1]["log_tail"])


def test_www_deployment_allows_any_safe_www_folder(client, monkeypatch, tmp_path):
    _setup_project(monkeypatch, tmp_path)
    target = tmp_path / "data" / "www" / "new-site"
    zip_path = tmp_path / "site.zip"
    _write_zip(zip_path, {"index.html": "new site"})

    response = client.post(
        "/api/v1/deploy/www/notice",
        json=_notice_payload(zip_path.as_uri(), folder="new-site"),
        headers=_headers(),
    )

    assert response.status_code == 200
    record = _records(tmp_path)[-1]
    assert record["status"] == "success"
    assert record["folder"] == "new-site"
    assert (target / "index.html").read_text(encoding="utf-8") == "new site"


def test_www_deployment_rejects_unsafe_folder(client, monkeypatch, tmp_path):
    _setup_project(monkeypatch, tmp_path)
    zip_path = tmp_path / "site.zip"
    _write_zip(zip_path, {"index.html": "hello"})

    response = client.post(
        "/api/v1/deploy/www/notice",
        json=_notice_payload(zip_path.as_uri(), folder="../bad"),
        headers=_headers(),
    )

    assert response.status_code == 200
    record = _records(tmp_path)[-1]
    assert record["status"] == "failed"
    assert "safe folder" in record["error"]


def test_www_deployment_rejects_zip_path_traversal(client, monkeypatch, tmp_path):
    _setup_project(monkeypatch, tmp_path)
    zip_path = tmp_path / "site.zip"
    _write_zip(zip_path, {"../index.html": "bad"})

    response = client.post(
        "/api/v1/deploy/www/notice",
        json=_notice_payload(zip_path.as_uri()),
        headers=_headers(),
    )

    assert response.status_code == 200
    record = _records(tmp_path)[-1]
    assert record["status"] == "failed"
    assert "unsafe path" in record["error"]


def test_www_deployment_rejects_missing_index(client, monkeypatch, tmp_path):
    _setup_project(monkeypatch, tmp_path)
    zip_path = tmp_path / "site.zip"
    _write_zip(zip_path, {"app.js": "console.log(1)"})

    response = client.post(
        "/api/v1/deploy/www/notice",
        json=_notice_payload(zip_path.as_uri()),
        headers=_headers(),
    )

    assert response.status_code == 200
    record = _records(tmp_path)[-1]
    assert record["status"] == "failed"
    assert "index.html" in record["error"]


def test_www_deployment_builds_github_artifact_api_request(monkeypatch):
    from services.operations.deployment import DeploymentService

    monkeypatch.setenv("DEPLOY_GITHUB_TOKEN", "github-token")

    request = DeploymentService._build_github_artifact_request(
        "https://github.com/acme/demo/actions/runs/123/artifacts/456"
    )

    assert request.full_url == "https://api.github.com/repos/acme/demo/actions/artifacts/456/zip"
    assert request.headers["Authorization"] == "Bearer github-token"


def test_www_deployment_retry_creates_new_record(monkeypatch, tmp_path):
    from core import ProjectConfig
    from services.operations.deployment import DeploymentService

    monkeypatch.setattr(ProjectConfig, "PROJECT_ROOT", str(tmp_path))
    (tmp_path / "data" / "db").mkdir(parents=True, exist_ok=True)

    original = DeploymentService.create_record({
        "folder": "demo",
        "artifact_url": "file:///tmp/site.zip",
    })

    retry = DeploymentService.retry_record(original["id"])

    assert retry["id"] != original["id"]
    assert retry["artifact_url"] == original["artifact_url"]
    assert retry["folder"] == "demo"
