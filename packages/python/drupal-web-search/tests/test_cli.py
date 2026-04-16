"""Tests for drupal_web_search.cli module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest  # pyright: ignore[reportMissingImports]

from drupal_web_search.cli import build_parser  # pyright: ignore[reportMissingImports]
from drupal_web_search.search import SearchResult  # pyright: ignore[reportMissingImports]


class TestBuildParser:
    def test_positional_query_required(self) -> None:
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parses_query(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["drupal cache"])
        assert args.query == "drupal cache"

    def test_parses_engine_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["query", "--engine", "exa"])
        assert args.engine == "exa"

    def test_parses_json_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["query", "--json"])
        assert args.json is True

    def test_parses_limit_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["query", "--limit", "5"])
        assert args.limit == 5

    def test_parses_verbose_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["query", "--verbose"])
        assert args.verbose is True

    def test_parses_config_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["query", "--config", "/path/to/config.toml"])
        assert str(args.config) == "/path/to/config.toml"

    def test_parses_single_site_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["query", "--site", "drupal.org"])
        assert args.site == ["drupal.org"]

    def test_parses_multiple_site_flags(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "query",
                "--site",
                "drupal.org",
                "--site",
                "drupalproject.org",
                "--site",
                "drupalcode.org",
            ]
        )
        assert args.site == ["drupal.org", "drupalproject.org", "drupalcode.org"]

    def test_site_empty_by_default(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["query"])
        assert args.site == []

    def test_parses_show_config_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["query", "--show-config"])
        assert args.show_config is True

    def test_combined_args(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "drupal cache tags",
                "--engine",
                "tavily",
                "--limit",
                "10",
                "--json",
                "--verbose",
                "--site",
                "github.com",
                "--site",
                "stackoverflow.com",
            ]
        )
        assert args.query == "drupal cache tags"
        assert args.engine == "tavily"
        assert args.limit == 10
        assert args.json is True
        assert args.verbose is True
        assert args.site == ["github.com", "stackoverflow.com"]


class TestLimitValidation:
    def test_limit_zero_rejected(self) -> None:
        from drupal_web_search.cli import main  # pyright: ignore[reportMissingImports]

        with patch("sys.argv", ["drupal-web-search", "query", "--limit", "0"]):
            with patch("drupal_web_search.cli.load_config") as mock_config:
                mock_config.return_value = MagicMock()
                with pytest.raises(SystemExit):
                    main()

    def test_limit_negative_rejected(self) -> None:
        from drupal_web_search.cli import main  # pyright: ignore[reportMissingImports]

        with patch("sys.argv", ["drupal-web-search", "query", "--limit", "-5"]):
            with patch("drupal_web_search.cli.load_config") as mock_config:
                mock_config.return_value = MagicMock()
                with pytest.raises(SystemExit):
                    main()


class TestMainOutput:
    def test_prints_results_text(self) -> None:
        from drupal_web_search.cli import main  # pyright: ignore[reportMissingImports]

        mock_config = MagicMock()
        mock_config.default_engine = "duckduckgo"
        mock_config.fallback_order = ()
        mock_config.search.num_results = 10
        mock_config.site_preferences.restrict_to = ()
        mock_config.search.safe_search = "moderate"
        mock_config.search.timeout = 30
        mock_config.engines = {}
        mock_config.site_preferences.preferred = ()
        mock_config.site_preferences.blocked = ()
        mock_config.config_path = MagicMock()

        mock_results = [
            SearchResult(
                title="Result 1", url="https://example.com", snippet="desc 1", engine="duckduckgo"
            ),
            SearchResult(
                title="Result 2", url="https://example.org", snippet="desc 2", engine="duckduckgo"
            ),
        ]

        with patch("sys.argv", ["drupal-web-search", "query"]):
            with patch("drupal_web_search.cli.load_config", return_value=mock_config):
                with patch("drupal_web_search.cli.search_web", return_value=mock_results):
                    with patch("sys.stdout") as mock_stdout:
                        main()
                        output = "".join(c[0][0] for c in mock_stdout.write.call_args_list)
                        assert "Result 1" in output
                        assert "https://example.com" in output
                        assert "duckduckgo" in output

    def test_prints_json(self) -> None:
        import json

        from drupal_web_search.cli import main  # pyright: ignore[reportMissingImports]

        mock_config = MagicMock()
        mock_config.default_engine = "duckduckgo"
        mock_config.fallback_order = ()
        mock_config.search.num_results = 10
        mock_config.site_preferences.restrict_to = ()
        mock_config.search.safe_search = "moderate"
        mock_config.search.timeout = 30
        mock_config.engines = {}
        mock_config.site_preferences.preferred = ()
        mock_config.site_preferences.blocked = ()
        mock_config.config_path = MagicMock()

        mock_results = [
            SearchResult(
                title="JSON Result",
                url="https://json.example",
                snippet="json desc",
                engine="tavily",
            ),
        ]

        with patch("sys.argv", ["drupal-web-search", "query", "--json"]):
            with patch("drupal_web_search.cli.load_config", return_value=mock_config):
                with patch("drupal_web_search.cli.search_web", return_value=mock_results):
                    with patch("sys.stdout") as mock_stdout:
                        main()
                        output = "".join(c[0][0] for c in mock_stdout.write.call_args_list)
                        parsed = json.loads(output)
                        assert len(parsed) == 1
                        assert parsed[0]["title"] == "JSON Result"

    def test_prints_no_results(self) -> None:
        from drupal_web_search.cli import main  # pyright: ignore[reportMissingImports]

        mock_config = MagicMock()
        mock_config.default_engine = "duckduckgo"
        mock_config.fallback_order = ()
        mock_config.search.num_results = 10
        mock_config.site_preferences.restrict_to = ()
        mock_config.search.safe_search = "moderate"
        mock_config.search.timeout = 30
        mock_config.engines = {}
        mock_config.site_preferences.preferred = ()
        mock_config.site_preferences.blocked = ()
        mock_config.config_path = MagicMock()

        with patch("sys.argv", ["drupal-web-search", "query"]):
            with patch("drupal_web_search.cli.load_config", return_value=mock_config):
                with patch("drupal_web_search.cli.search_web", return_value=[]):
                    with patch("sys.stdout") as mock_stdout:
                        main()
                        output = "".join(c[0][0] for c in mock_stdout.write.call_args_list)
                        assert "No results found" in output

    def test_prints_error_on_failure(self) -> None:
        from drupal_web_search.cli import main  # pyright: ignore[reportMissingImports]

        mock_config = MagicMock()
        mock_config.default_engine = "duckduckgo"
        mock_config.fallback_order = ()
        mock_config.search.num_results = 10
        mock_config.site_preferences.restrict_to = ()
        mock_config.search.safe_search = "moderate"
        mock_config.search.timeout = 30
        mock_config.engines = {}
        mock_config.site_preferences.preferred = ()
        mock_config.site_preferences.blocked = ()
        mock_config.config_path = MagicMock()

        with patch("sys.argv", ["drupal-web-search", "query"]):
            with patch("drupal_web_search.cli.load_config", return_value=mock_config):
                with patch(
                    "drupal_web_search.cli.search_web",
                    side_effect=RuntimeError("Search failed"),
                ):
                    with patch("sys.stderr") as mock_stderr:
                        result = main()
                        output = "".join(c[0][0] for c in mock_stderr.write.call_args_list)
                        assert result == 1
                        assert "Search failed" in output

    def test_passes_site_to_search_web(self) -> None:
        from drupal_web_search.cli import main  # pyright: ignore[reportMissingImports]

        mock_config = MagicMock()
        mock_config.default_engine = "duckduckgo"
        mock_config.fallback_order = ()
        mock_config.search.num_results = 10
        mock_config.site_preferences.restrict_to = ()
        mock_config.search.safe_search = "moderate"
        mock_config.search.timeout = 30
        mock_config.engines = {}
        mock_config.site_preferences.preferred = ()
        mock_config.site_preferences.blocked = ()
        mock_config.config_path = MagicMock()

        with patch(
            "sys.argv",
            ["drupal-web-search", "query", "--site", "drupal.org", "--site", "github.com"],
        ):
            with patch("drupal_web_search.cli.load_config", return_value=mock_config):
                with patch("drupal_web_search.cli.search_web") as mock_search:
                    mock_search.return_value = []
                    main()
                    _, kwargs = mock_search.call_args
                    assert kwargs["site"] == ["drupal.org", "github.com"]

    def test_show_config_prints_and_exits(self) -> None:
        from drupal_web_search.cli import main  # pyright: ignore[reportMissingImports]

        mock_config = MagicMock()
        mock_config.default_engine = "tavily"
        mock_config.fallback_order = ("brave",)
        mock_config.search.num_results = 20
        mock_config.site_preferences.restrict_to = ("drupal.org",)
        mock_config.search.safe_search = "off"
        mock_config.search.timeout = 60
        mock_config.engines = {
            "duckduckgo": MagicMock(enabled=True),
            "tavily": MagicMock(enabled=False),
        }
        mock_config.site_preferences.restrict_to = ("drupal.org",)
        mock_config.site_preferences.preferred = ("github.com",)
        mock_config.site_preferences.blocked = ()
        mock_config.config_path = "/path/to/config.toml"

        with patch("sys.argv", ["drupal-web-search", "query", "--show-config"]):
            with patch("drupal_web_search.cli.load_config", return_value=mock_config):
                with patch("sys.stdout") as mock_stdout:
                    result = main()
                    output = "".join(c[0][0] for c in mock_stdout.write.call_args_list)
                    assert result == 0
                    assert "Config file: /path/to/config.toml" in output
                    assert "Default engine: tavily" in output
                    assert "Fallback order: ('brave',)" in output
                    assert "Search num_results: 20" in output
                    assert "Site preferences restrict_to: ('drupal.org',)" in output

    def test_verbose_prints_engine_info(self) -> None:
        from drupal_web_search.cli import main  # pyright: ignore[reportMissingImports]

        mock_config = MagicMock()
        mock_config.default_engine = "tavily"
        mock_config.fallback_order = ("exa", "perplexity")
        mock_config.search.num_results = 10
        mock_config.site_preferences.restrict_to = ()
        mock_config.search.safe_search = "moderate"
        mock_config.search.timeout = 30
        mock_config.engines = {}
        mock_config.site_preferences.preferred = ()
        mock_config.site_preferences.blocked = ()
        mock_config.config_path = MagicMock()

        with patch("sys.argv", ["drupal-web-search", "query", "--engine", "tavily", "--verbose"]):
            with patch("drupal_web_search.cli.load_config", return_value=mock_config):
                with patch("drupal_web_search.cli.search_web", return_value=[]):
                    with patch("sys.stderr") as mock_stderr:
                        main()
                        output = "".join(c[0][0] for c in mock_stderr.write.call_args_list)
                        assert "Engine: tavily" in output
                        assert "--engine overrides" in output
