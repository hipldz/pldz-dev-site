import json
import subprocess
from pathlib import Path


def test_shell_migration_moves_legacy_files_and_extracts_article_views(tmp_path):
    script = Path(__file__).resolve().parents[2] / "migrate-data.sh"
    legacy_db = tmp_path / "data" / "db" / "articles.json"
    legacy_resource = tmp_path / "data" / "resources" / "privacy_policy.txt"
    legacy_webp = tmp_path / "data" / "webp" / "thumbnail.webp"
    legacy_db.parent.mkdir(parents=True, exist_ok=True)
    legacy_db.write_text(json.dumps({"article-one": {"views": 17}}), encoding="utf-8")
    for file_path in (legacy_resource, legacy_webp):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file_path.name, encoding="utf-8")

    subprocess.run([str(script), str(tmp_path)], check=True)

    views_path = tmp_path / "data" / "db" / "content" / "article_views.json"
    assert json.loads(views_path.read_text(encoding="utf-8")) == {"article-one": 17}
    assert (tmp_path / "data" / "migration-backup" / "articles.json").is_file()
    assert (tmp_path / "data" / "resources" / "website" / "legal" / "privacy_policy.txt").is_file()
    assert (tmp_path / "data" / "cache" / "webp" / "thumbnail.webp").is_file()
    assert not (tmp_path / "data" / "webp").exists()
