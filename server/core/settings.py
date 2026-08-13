import os
from dataclasses import dataclass
from typing import Mapping


_PLACEHOLDER_VALUES = {
    "ADMIN_PASSWORD": {"123", "change-me"},
    "CACHE_API_TOKEN": {"change-me"},
    "DEPLOY_GITHUB_TOKEN": {"github_pat_xxx", "change-me"},
    "DEPLOY_NOTICE_TOKEN": {"change-me"},
    "SECRET_KEY": {"your-super-secret-key", "change-me"},
}


@dataclass(frozen=True)
class Settings:
    """Typed snapshot of application environment variables.

    Invalid or missing values are reported through ``warnings`` and fall back to
    the application's existing defaults. Configuration inspection never exposes
    the value of a secret.
    """

    articles_path: str
    images_path: str
    resources_path: str
    cache_path: str
    webp_cache_path: str
    db_path: str
    www_path: str

    deploy_notice_token: str
    deploy_github_token: str
    deploy_max_artifact_bytes: int
    deploy_http_proxy: str
    deploy_https_proxy: str
    cache_api_token: str

    secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    two_factor_issuer: str
    admin_username: str
    admin_password: str

    site_host: str
    site_port: int
    site_name: str
    site_copyright: str
    site_icp: str
    site_ps: str

    image_process_concurrency: int
    webp_method: int

    warnings: tuple[str, ...] = ()

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str, str] | None = None,
        initial_warnings: tuple[str, ...] = (),
    ) -> "Settings":
        source = os.environ if environ is None else environ
        missing: list[str] = []
        invalid: list[str] = []

        def text(name: str, default: str = "", *, report_missing: bool = True) -> str:
            value = source.get(name)
            if value is None or not value.strip():
                if report_missing:
                    missing.append(name)
                return default
            return value.strip()

        def positive_int(name: str, default: int, *, maximum: int | None = None) -> int:
            raw = source.get(name)
            if raw is None or not raw.strip():
                missing.append(name)
                return default
            try:
                value = int(raw)
            except ValueError:
                invalid.append(name)
                return default
            if value <= 0 or (maximum is not None and value > maximum):
                invalid.append(name)
                return default
            return value

        values = {
            "articles_path": text("ARTICLES_PATH", "data/articles"),
            "images_path": text("IMAGES_PATH", "data/images"),
            "resources_path": text("RESOURCES_PATH", "data/resources"),
            "cache_path": text("CACHE_PATH", "data/cache"),
            "webp_cache_path": text("WEBP_CACHE_PATH", "data/cache/webp"),
            "db_path": text("DB_PATH", "data/db"),
            "www_path": text("WWW_PATH", "data/www"),
            "deploy_notice_token": text("DEPLOY_NOTICE_TOKEN", report_missing=False),
            "deploy_github_token": text("DEPLOY_GITHUB_TOKEN", report_missing=False),
            "deploy_max_artifact_bytes": positive_int("DEPLOY_MAX_ARTIFACT_BYTES", 104857600),
            "deploy_http_proxy": text("DEPLOY_HTTP_PROXY", report_missing=False),
            "deploy_https_proxy": text("DEPLOY_HTTPS_PROXY", report_missing=False),
            "cache_api_token": text("CACHE_API_TOKEN", report_missing=False),
            "secret_key": text("SECRET_KEY", report_missing=False),
            "access_token_expire_minutes": positive_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30),
            "refresh_token_expire_days": positive_int("REFRESH_TOKEN_EXPIRE_DAYS", 7),
            "two_factor_issuer": text("TWO_FACTOR_ISSUER", "pldz-dev-site"),
            "admin_username": text("ADMIN_USERNAME", "admin@pldz1.com"),
            "admin_password": text("ADMIN_PASSWORD", "123", report_missing=False),
            "site_host": text("SITE_HOST", "127.0.0.1"),
            "site_port": positive_int("SITE_PORT", 10058, maximum=65535),
            "site_name": text("SITE_NAME", "爬楼的猪 Dev"),
            "site_copyright": text("SITE_COPYRIGHT", "Copyright信息未设置"),
            "site_icp": text("SITE_ICP", "ICP信息未设置"),
            "site_ps": text("SITE_PS", "PS信息未设置"),
            "image_process_concurrency": positive_int("IMAGE_PROCESS_CONCURRENCY", 2),
            "webp_method": positive_int("WEBP_METHOD", 4, maximum=6),
        }

        insecure = [
            name
            for name, placeholders in _PLACEHOLDER_VALUES.items()
            if not source.get(name, "").strip() or source.get(name, "").strip() in placeholders
        ]

        messages = list(initial_warnings)
        if missing:
            messages.append(f"未配置，正在使用默认值: {', '.join(sorted(missing))}")
        if invalid:
            messages.append(f"配置值无效，已回退到默认值: {', '.join(sorted(invalid))}")
        if insecure:
            messages.append(f"敏感配置未设置或仍为示例值: {', '.join(sorted(insecure))}")

        return cls(**values, warnings=tuple(messages))
