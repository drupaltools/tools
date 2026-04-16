"""Tests for drupal_web_search.search module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest  # pyright: ignore[reportMissingImports]

from drupal_web_search.config import (  # pyright: ignore[reportMissingImports]
    AppConfig,
    EngineSettings,
    SearchSettings,
    SitePreferences,
)
from drupal_web_search.search import (  # pyright: ignore[reportMissingImports]
    SearchResult,
    _run_engine,
    apply_site_preferences,
    build_engine_order,
    normalize_results,
    search_web,
)


def make_config(
    default_engine: str = "duckduckgo",
    fallback_order: tuple[str, ...] = (),
    engines: dict[str, EngineSettings] | None = None,
    search_settings: SearchSettings | None = None,
    site_preferences: SitePreferences | None = None,
) -> AppConfig:
    return AppConfig(
        default_engine=default_engine,
        fallback_order=fallback_order,
        engines=engines
        or {
            "duckduckgo": EngineSettings(name="duckduckgo", enabled=True),
            "brave": EngineSettings(name="brave", enabled=True),
            "exa": EngineSettings(name="exa", enabled=True, api_key="test-key"),
            "tavily": EngineSettings(name="tavily", enabled=True, api_key="test-key"),
            "firecrawl": EngineSettings(name="firecrawl", enabled=True, api_key="test-key"),
            "serpapi": EngineSettings(name="serpapi", enabled=True, api_key="test-key"),
            "perplexity": EngineSettings(name="perplexity", enabled=True, api_key="test-key"),
        },
        search=search_settings
        or SearchSettings(num_results=10, safe_search="moderate", timeout=30),
        site_preferences=site_preferences
        or SitePreferences(restrict_to=(), preferred=(), blocked=()),
        config_path=None,
    )


class TestBuildEngineOrder:
    def test_respects_requested_engine(self) -> None:
        config = make_config(default_engine="duckduckgo", fallback_order=("brave",))
        assert build_engine_order(config, requested_engine="brave") == ["brave"]

    def test_skips_disabled_engines(self) -> None:
        config = make_config(
            engines={
                "duckduckgo": EngineSettings(name="duckduckgo", enabled=True),
                "brave": EngineSettings(name="brave", enabled=False),
            },
        )
        assert build_engine_order(config) == ["duckduckgo"]

    def test_deduplicates_across_default_and_fallback(self) -> None:
        config = make_config(
            default_engine="duckduckgo",
            fallback_order=("brave", "duckduckgo"),
        )
        result = build_engine_order(config)
        assert result.count("duckduckgo") == 1

    def test_requested_engine_unknown_raises(self) -> None:
        config = make_config(
            engines={"duckduckgo": EngineSettings(name="duckduckgo", enabled=True)},
        )
        with pytest.raises(ValueError, match="Unknown engine"):
            build_engine_order(config, requested_engine="dasdsa")

    def test_requested_engine_disabled_raises(self) -> None:
        config = make_config(
            engines={"brave": EngineSettings(name="brave", enabled=False)},
        )
        with pytest.raises(ValueError, match="disabled"):
            build_engine_order(config, requested_engine="brave")

    def test_fallback_skips_unknown_and_disabled(self) -> None:
        config = make_config(
            engines={"duckduckgo": EngineSettings(name="duckduckgo", enabled=True)},
            fallback_order=("unknown_engine", "brave"),
        )
        assert build_engine_order(config) == ["duckduckgo"]

    def test_no_enabled_engines_raises(self) -> None:
        config = make_config(
            engines={"duckduckgo": EngineSettings(name="duckduckgo", enabled=False)},
        )
        with pytest.raises(ValueError, match="No enabled engines"):
            build_engine_order(config)


class TestNormalizeResults:
    def test_maps_ddgs_fields(self) -> None:
        raw = [
            {"href": "https://example.com", "title": "Example", "body": "description"},
        ]
        results = normalize_results(raw, "duckduckgo")
        assert len(results) == 1
        assert results[0].url == "https://example.com"
        assert results[0].title == "Example"
        assert results[0].snippet == "description"
        assert results[0].engine == "duckduckgo"

    def test_skips_items_without_url(self) -> None:
        raw = [{"title": "No URL"}, {"href": "", "title": "Empty URL"}]
        results = normalize_results(raw, "duckduckgo")
        assert results == []

    def test_uses_url_as_fallback_title(self) -> None:
        raw = [{"href": "https://example.com"}]
        results = normalize_results(raw, "duckduckgo")
        assert results[0].title == "https://example.com"


class TestApplySitePreferences:
    def test_blocks_specified_domains(self) -> None:
        config = make_config(
            site_preferences=SitePreferences(restrict_to=(), preferred=(), blocked=("spam.com",)),
        )
        results = [
            SearchResult("Good", "https://good.com", "", "ddgs"),
            SearchResult("Bad", "https://spam.com", "", "ddgs"),
        ]
        filtered = apply_site_preferences(results, config)
        assert [r.title for r in filtered] == ["Good"]

    def test_boosts_preferred_domains(self) -> None:
        config = make_config(
            site_preferences=SitePreferences(restrict_to=(), preferred=("github.com",), blocked=()),
        )
        results = [
            SearchResult("Other", "https://other.com", "", "ddgs"),
            SearchResult("GitHub", "https://github.com/drupal", "", "ddgs"),
        ]
        filtered = apply_site_preferences(results, config)
        assert filtered[0].title == "GitHub"
        assert filtered[1].title == "Other"

    def test_deduplicates_by_url(self) -> None:
        config = make_config(
            site_preferences=SitePreferences(restrict_to=(), preferred=(), blocked=())
        )
        results = [
            SearchResult("First", "https://example.com", "", "ddgs"),
            SearchResult("Dup", "https://example.com", "", "ddgs"),
        ]
        filtered = apply_site_preferences(results, config)
        assert len(filtered) == 1


class TestRunEngine:
    def test_routes_to_ddgs(self) -> None:
        mock_results = [
            {"href": "https://example.com", "title": "Example", "body": "desc"},
        ]
        mock_client = MagicMock()
        mock_client.text.return_value = mock_results
        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_client
        mock_ddgs.return_value.__exit__.return_value = None

        with patch("drupal_web_search.search.DDGS", mock_ddgs):
            results = _run_engine("duckduckgo", "query", 10, make_config())

        assert len(results) == 1
        assert results[0].url == "https://example.com"
        mock_ddgs.return_value.__enter__.return_value.text.assert_called_once()

    def test_routes_to_brave_ddgs_backend(self) -> None:
        mock_results = [{"href": "https://brave.example", "title": "Brave", "body": "b"}]
        mock_client = MagicMock()
        mock_client.text.return_value = mock_results
        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_client
        mock_ddgs.return_value.__exit__.return_value = None

        with patch("drupal_web_search.search.DDGS", mock_ddgs):
            results = _run_engine("brave", "query", 10, make_config())

        assert results[0].engine == "brave"
        mock_client.text.assert_called_once()
        _, kwargs = mock_client.text.call_args
        assert kwargs["backend"] == "brave"

    def test_routes_to_exa(self) -> None:
        mock_result = MagicMock()
        mock_result.title = "Exa Result"
        mock_result.url = "https://exa.example"
        mock_result.highlights = ["highlight text"]

        mock_results = [
            SearchResult(
                title="Exa Result",
                url="https://exa.example",
                snippet="highlight text",
                engine="exa",
            )
        ]

        with patch("drupal_web_search.search._search_exa", return_value=mock_results):
            with patch("drupal_web_search.search._EXA_AVAILABLE", True):
                results = _run_engine("exa", "query", 10, make_config())

        assert len(results) == 1
        assert results[0].title == "Exa Result"

    def test_exa_raises_when_not_available(self) -> None:
        with patch("drupal_web_search.search._EXA_AVAILABLE", False):
            with pytest.raises(ImportError, match="exa-py"):
                _run_engine("exa", "query", 10, make_config())

    def test_exa_raises_when_no_api_key(self) -> None:
        config = make_config(
            engines={"exa": EngineSettings(name="exa", enabled=True, api_key="")},
        )
        with patch("drupal_web_search.search._EXA_AVAILABLE", True):
            with pytest.raises(ValueError, match="EXA_API_KEY"):
                _run_engine("exa", "query", 10, config)

    def test_routes_to_tavily(self) -> None:
        mock_results = [
            SearchResult(
                title="Tavily Result",
                url="https://tavily.example",
                snippet="content text",
                engine="tavily",
            )
        ]

        with patch("drupal_web_search.search._search_tavily", return_value=mock_results):
            with patch("drupal_web_search.search._TAVILY_AVAILABLE", True):
                results = _run_engine("tavily", "query", 10, make_config())

        assert len(results) == 1
        assert results[0].title == "Tavily Result"
        assert results[0].engine == "tavily"

    def test_tavily_raises_when_not_available(self) -> None:
        with patch("drupal_web_search.search._TAVILY_AVAILABLE", False):
            with pytest.raises(ImportError, match="tavily-python"):
                _run_engine("tavily", "query", 10, make_config())

    def test_tavily_raises_when_no_api_key(self) -> None:
        config = make_config(
            engines={"tavily": EngineSettings(name="tavily", enabled=True, api_key="")},
        )
        with patch("drupal_web_search.search._TAVILY_AVAILABLE", True):
            with pytest.raises(ValueError, match="TAVILY_API_KEY"):
                _run_engine("tavily", "query", 10, config)

    def test_routes_to_firecrawl(self) -> None:
        mock_results = [
            SearchResult(
                title="Firecrawl Result",
                url="https://firecrawl.example",
                snippet="desc text",
                engine="firecrawl",
            )
        ]

        with patch("drupal_web_search.search._search_firecrawl", return_value=mock_results):
            with patch("drupal_web_search.search._FIRECRAWL_AVAILABLE", True):
                results = _run_engine("firecrawl", "query", 10, make_config())

        assert len(results) == 1
        assert results[0].title == "Firecrawl Result"
        assert results[0].engine == "firecrawl"

    def test_firecrawl_raises_when_not_available(self) -> None:
        with patch("drupal_web_search.search._FIRECRAWL_AVAILABLE", False):
            with pytest.raises(ImportError, match="firecrawl-py"):
                _run_engine("firecrawl", "query", 10, make_config())

    def test_firecrawl_raises_when_no_api_key(self) -> None:
        config = make_config(
            engines={"firecrawl": EngineSettings(name="firecrawl", enabled=True, api_key="")},
        )
        with patch("drupal_web_search.search._FIRECRAWL_AVAILABLE", True):
            with pytest.raises(ValueError, match="FIRECRAWL_API_KEY"):
                _run_engine("firecrawl", "query", 10, config)

    def test_routes_to_serpapi(self) -> None:
        mock_results = [
            SearchResult(
                title="SerpAPI Result",
                url="https://serpapi.example",
                snippet="serp snippet",
                engine="serpapi",
            )
        ]

        with patch("drupal_web_search.search._search_serpapi", return_value=mock_results):
            with patch("drupal_web_search.search._SERPAPI_AVAILABLE", True):
                results = _run_engine("serpapi", "query", 10, make_config())

        assert len(results) == 1
        assert results[0].title == "SerpAPI Result"
        assert results[0].engine == "serpapi"

    def test_serpapi_raises_when_not_available(self) -> None:
        with patch("drupal_web_search.search._SERPAPI_AVAILABLE", False):
            with pytest.raises(ImportError, match="serpapi"):
                _run_engine("serpapi", "query", 10, make_config())

    def test_serpapi_raises_when_no_api_key(self) -> None:
        config = make_config(
            engines={"serpapi": EngineSettings(name="serpapi", enabled=True, api_key="")},
        )
        with patch("drupal_web_search.search._SERPAPI_AVAILABLE", True):
            with pytest.raises(ValueError, match="SERPAPI_API_KEY"):
                _run_engine("serpapi", "query", 10, config)

    def test_routes_to_perplexity(self) -> None:
        mock_results = [
            SearchResult(
                title="Perplexity Result",
                url="https://perplexity.example",
                snippet="perp desc",
                engine="perplexity",
            )
        ]

        with patch("drupal_web_search.search._search_perplexity", return_value=mock_results):
            with patch("drupal_web_search.search._PERPLEXITY_AVAILABLE", True):
                results = _run_engine("perplexity", "query", 10, make_config())

        assert len(results) == 1
        assert results[0].title == "Perplexity Result"
        assert results[0].engine == "perplexity"

    def test_perplexity_raises_when_not_available(self) -> None:
        with patch("drupal_web_search.search._PERPLEXITY_AVAILABLE", False):
            with pytest.raises(ImportError, match="perplexityai"):
                _run_engine("perplexity", "query", 10, make_config())

    def test_perplexity_raises_when_no_api_key(self) -> None:
        config = make_config(
            engines={"perplexity": EngineSettings(name="perplexity", enabled=True, api_key="")},
        )
        with patch("drupal_web_search.search._PERPLEXITY_AVAILABLE", True):
            with pytest.raises(ValueError, match="PERPLEXITY_API_KEY"):
                _run_engine("perplexity", "query", 10, config)

    def test_unknown_engine_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown engine"):
            _run_engine("unknown_engine", "query", 10, make_config())


class TestRunEngineFallback:
    def test_falls_back_to_second_engine_on_exception(self) -> None:
        config = make_config(
            default_engine="duckduckgo",
            fallback_order=("brave",),
        )
        mock_results = [
            {"href": "https://fallback.example", "title": "Fallback", "body": "fallback desc"},
        ]
        mock_client = MagicMock()
        mock_client.text.return_value = mock_results
        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_client
        mock_ddgs.return_value.__exit__.return_value = None

        call_count = [0]

        def ddgs_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("network error")
            return mock_ddgs.return_value

        mock_ddgs.side_effect = ddgs_side_effect

        with patch("drupal_web_search.search.DDGS", mock_ddgs):
            results = search_web("query", config)

        assert len(results) == 1
        assert results[0].title == "Fallback"
        assert call_count[0] == 2

    def test_raises_after_all_engines_fail(self) -> None:
        config = make_config(
            default_engine="duckduckgo",
            fallback_order=(),
        )

        def always_fail(*args, **kwargs):
            raise RuntimeError("always fails")

        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.return_value.text.side_effect = always_fail
        mock_ddgs.return_value.__exit__.return_value = None

        with patch("drupal_web_search.search.DDGS", mock_ddgs):
            with pytest.raises(RuntimeError, match="Search failed for all configured engines"):
                search_web("query", config)


class TestSearchWebSiteParam:
    def test_cli_site_flag_prepends_to_query(self) -> None:
        mock_results = [
            {"href": "https://example.com", "title": "Example", "body": "desc"},
        ]
        mock_client = MagicMock()
        mock_client.text.return_value = mock_results
        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_client
        mock_ddgs.return_value.__exit__.return_value = None

        with patch("drupal_web_search.search.DDGS", mock_ddgs):
            search_web("drupal cache", make_config(), site=["drupal.org"])

        call_args = mock_client.text.call_args
        assert "site:drupal.org" in call_args[0][0]
        assert "drupal cache" in call_args[0][0]

    def test_multiple_cli_sites(self) -> None:
        mock_client = MagicMock()
        mock_client.text.return_value = []
        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_client
        mock_ddgs.return_value.__exit__.return_value = None

        with patch("drupal_web_search.search.DDGS", mock_ddgs):
            search_web("query", make_config(), site=["drupal.org", "drupalproject.org"])

        call_args = mock_client.text.call_args[0][0]
        assert "site:drupal.org" in call_args
        assert "site:drupalproject.org" in call_args

    def test_config_restrict_to_combines_with_cli(self) -> None:
        mock_client = MagicMock()
        mock_client.text.return_value = []
        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_client
        mock_ddgs.return_value.__exit__.return_value = None

        config = make_config(
            site_preferences=SitePreferences(
                restrict_to=("drupalproject.org",),
                preferred=(),
                blocked=(),
            ),
        )

        with patch("drupal_web_search.search.DDGS", mock_ddgs):
            search_web("query", config, site=["drupal.org"])

        call_args = mock_client.text.call_args[0][0]
        assert "site:drupal.org" in call_args
        assert "site:drupalproject.org" in call_args

    def test_no_site_means_no_prefix(self) -> None:
        mock_client = MagicMock()
        mock_client.text.return_value = [
            {"href": "https://example.com", "title": "Example", "body": ""},
        ]
        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_client
        mock_ddgs.return_value.__exit__.return_value = None

        with patch("drupal_web_search.search.DDGS", mock_ddgs):
            search_web("drupal cache", make_config(), site=None)

        call_args = mock_client.text.call_args[0][0]
        assert call_args == "drupal cache"
        assert "site:" not in call_args

    def test_empty_site_list_no_prefix(self) -> None:
        mock_client = MagicMock()
        mock_client.text.return_value = [
            {"href": "https://example.com", "title": "Example", "body": ""},
        ]
        mock_ddgs = MagicMock()
        mock_ddgs.return_value.__enter__.return_value = mock_client
        mock_ddgs.return_value.__exit__.return_value = None

        with patch("drupal_web_search.search.DDGS", mock_ddgs):
            search_web("drupal cache", make_config(), site=[])

        call_args = mock_client.text.call_args[0][0]
        assert call_args == "drupal cache"
