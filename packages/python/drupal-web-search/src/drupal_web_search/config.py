"""Configuration loading for drupal_web_search."""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # pyright: ignore[reportMissingImports]

ENV_VAR_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")


@dataclass(frozen=True)
class EngineSettings:
    name: str
    enabled: bool
    api_key: str = ""
    model: str = ""


@dataclass(frozen=True)
class SearchSettings:
    num_results: int
    safe_search: str
    timeout: int


@dataclass(frozen=True)
class SitePreferences:
    restrict_to: tuple[str, ...]
    preferred: tuple[str, ...]
    blocked: tuple[str, ...]


@dataclass(frozen=True)
class AppConfig:
    default_engine: str
    fallback_order: tuple[str, ...]
    engines: dict[str, EngineSettings]
    search: SearchSettings
    site_preferences: SitePreferences
    config_path: Path


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key and key not in os.environ:
            os.environ[key] = value


def find_package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def find_default_config_path() -> Path:
    package_root_config = find_package_root() / "config.toml"
    if package_root_config.exists():
        return package_root_config

    working_dir_config = Path.cwd() / "config.toml"
    if working_dir_config.exists():
        return working_dir_config

    bundled_path = resources.files("drupal_web_search").joinpath("config.toml")
    return Path(str(bundled_path))


def expand_env_values(value: Any) -> Any:
    if isinstance(value, str):
        return ENV_VAR_PATTERN.sub(lambda match: os.environ.get(match.group(1), ""), value)
    if isinstance(value, list):
        return [expand_env_values(item) for item in value]
    if isinstance(value, dict):
        return {key: expand_env_values(item) for key, item in value.items()}
    return value


def load_config(config_path: Path | None = None) -> AppConfig:
    package_root = find_package_root()
    load_env_file(package_root / ".env")
    load_env_file(Path.cwd() / ".env")

    resolved_path = config_path or find_default_config_path()
    raw_config = tomllib.loads(resolved_path.read_text(encoding="utf-8"))
    expanded_config = expand_env_values(raw_config)

    engines_section = expanded_config.get("engines", {})
    default_engine = str(engines_section.get("default", "duckduckgo"))
    fallback_order = tuple(engines_section.get("fallback_order", []))

    engine_settings: dict[str, EngineSettings] = {}
    for name, values in engines_section.items():
        if name in {"default", "fallback_order"}:
            continue
        if not isinstance(values, dict):
            raise ValueError(f"Engine configuration for '{name}' must be a table.")
        engine_settings[name] = EngineSettings(
            name=name,
            enabled=bool(values.get("enabled", True)),
            api_key=str(values.get("api_key", "")),
            model=str(values.get("model", "")),
        )

    if default_engine not in engine_settings:
        raise ValueError(f"Default engine '{default_engine}' is not configured.")

    search_section = expanded_config.get("search", {})
    safe_search = str(search_section.get("safe_search", "moderate"))
    if safe_search not in {"on", "moderate", "off"}:
        raise ValueError("search.safe_search must be one of: on, moderate, off.")

    site_preferences_section = expanded_config.get("site_preferences", {})
    return AppConfig(
        default_engine=default_engine,
        fallback_order=fallback_order,
        engines=engine_settings,
        search=SearchSettings(
            num_results=int(search_section.get("num_results", 10)),
            safe_search=safe_search,
            timeout=int(search_section.get("timeout", 30)),
        ),
        site_preferences=SitePreferences(
            restrict_to=tuple(site_preferences_section.get("restrict_to", [])),
            preferred=tuple(site_preferences_section.get("preferred", [])),
            blocked=tuple(site_preferences_section.get("blocked", [])),
        ),
        config_path=resolved_path,
    )
