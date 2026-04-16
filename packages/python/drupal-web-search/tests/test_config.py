from pathlib import Path

import pytest  # pyright: ignore[reportMissingImports]

from drupal_web_search.config import load_config  # pyright: ignore[reportMissingImports]


def test_load_config_expands_env_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("BRAVE_API_KEY", "brave-secret")
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[engines]
default = "duckduckgo"
fallback_order = ["brave"]

[engines.duckduckgo]
enabled = true

[engines.brave]
enabled = true
api_key = "${BRAVE_API_KEY}"

[search]
num_results = 5
safe_search = "moderate"
timeout = 12

[site_preferences]
preferred = ["github.com"]
blocked = ["spam-site.com"]
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.engines["brave"].api_key == "brave-secret"
    assert config.search.num_results == 5
    assert config.site_preferences.preferred == ("github.com",)
