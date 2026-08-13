from pathlib import Path

from core import ProjectConfig, Settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class RecordingEnv(dict):
    def __init__(self):
        super().__init__()
        self.requested_names: set[str] = set()

    def get(self, key, default=None):
        self.requested_names.add(key)
        return super().get(key, default)


def test_env_example_matches_settings_contract():
    environ = RecordingEnv()
    Settings.from_env(environ)

    example_names = {
        line.split("=", 1)[0].strip()
        for line in (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }

    assert example_names == environ.requested_names


def test_settings_reports_missing_values_without_failing():
    settings = Settings.from_env({})

    assert settings.site_port == 10058
    assert settings.image_process_concurrency == 2
    assert any("未配置" in warning and "SITE_PORT" in warning for warning in settings.warnings)
    assert any("敏感配置" in warning and "SECRET_KEY" in warning for warning in settings.warnings)


def test_settings_reports_invalid_values_and_uses_defaults():
    settings = Settings.from_env({
        "SITE_PORT": "not-a-port",
        "IMAGE_PROCESS_CONCURRENCY": "0",
        "WEBP_METHOD": "4",
    })

    assert settings.site_port == 10058
    assert settings.image_process_concurrency == 2
    assert any(
        "配置值无效" in warning
        and "SITE_PORT" in warning
        and "IMAGE_PROCESS_CONCURRENCY" in warning
        for warning in settings.warnings
    )


def test_settings_warnings_do_not_contain_secret_values():
    secret = "a-private-secret-that-must-not-be-logged"
    settings = Settings.from_env({"SECRET_KEY": secret})

    assert all(secret not in warning for warning in settings.warnings)


def test_missing_env_file_no_longer_stops_startup(monkeypatch, tmp_path):
    monkeypatch.setattr(
        ProjectConfig,
        "get_abs_path",
        classmethod(lambda cls, folder="", file_name="": str(tmp_path / file_name)),
    )

    settings = ProjectConfig.load_env()

    assert settings is ProjectConfig.settings
    assert any(".env 未找到" in warning for warning in settings.warnings)
