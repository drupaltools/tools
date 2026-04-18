"""Search orchestration for drupal_web_search."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from urllib.parse import urlparse

from ddgs import DDGS  # pyright: ignore[reportMissingImports]

from drupal_web_search.config import AppConfig, EngineSettings

try:
    from exa_py import Exa  # pyright: ignore[reportMissingImports]

    _EXA_AVAILABLE = True
except ImportError:
    _EXA_AVAILABLE = False

try:
    from tavily import TavilyClient  # pyright: ignore[reportMissingImports]

    _TAVILY_AVAILABLE = True
except ImportError:
    _TAVILY_AVAILABLE = False

try:
    import perplexity  # pyright: ignore[reportMissingImports]

    _PERPLEXITY_AVAILABLE = True
except ImportError:
    _PERPLEXITY_AVAILABLE = False

try:
    import firecrawl  # pyright: ignore[reportMissingImports]

    _FIRECRAWL_AVAILABLE = True
except ImportError:
    _FIRECRAWL_AVAILABLE = False

try:
    import serpapi  # pyright: ignore[reportMissingImports]

    _SERPAPI_AVAILABLE = True
except ImportError:
    _SERPAPI_AVAILABLE = False

try:
    from linkup import LinkupClient  # pyright: ignore[reportMissingImports]

    _LINKUP_AVAILABLE = True
except ImportError:
    _LINKUP_AVAILABLE = False

try:
    import httpx

    _JINA_AVAILABLE = True
except ImportError:
    _JINA_AVAILABLE = False




@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    engine: str


def build_engine_order(config: AppConfig, requested_engine: str | None = None) -> list[str]:
    if requested_engine:
        if requested_engine not in config.engines:
            raise ValueError(
                f"Unknown engine: '{requested_engine}'. Available: {', '.join(config.engines)}"
            )
        if not config.engines[requested_engine].enabled:
            raise ValueError(f"Engine '{requested_engine}' is disabled.")
        return [requested_engine]

    candidates = [config.default_engine]
    candidates.extend(config.fallback_order)

    ordered_engines: list[str] = []
    for engine_name in candidates:
        if not engine_name or engine_name in ordered_engines:
            continue
        settings = config.engines.get(engine_name)
        if settings and settings.enabled:
            ordered_engines.append(engine_name)

    if ordered_engines:
        return ordered_engines

    raise ValueError("No enabled engines are available from the requested configuration.")


def extract_domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def domain_matches(domain: str, candidates: Iterable[str]) -> bool:
    for candidate in candidates:
        normalized = candidate.lower().removeprefix("www.")
        if domain == normalized or domain.endswith(f".{normalized}"):
            return True
    return False


def normalize_results(raw_results: list[dict[str, str]], engine: str) -> list[SearchResult]:
    normalized_results: list[SearchResult] = []
    for item in raw_results:
        url = item.get("href", "").strip()
        if not url:
            continue
        normalized_results.append(
            SearchResult(
                title=item.get("title", "").strip() or url,
                url=url,
                snippet=item.get("body", "").strip(),
                engine=engine,
            )
        )
    return normalized_results


def _run_engine(engine: str, query: str, limit: int, config: AppConfig, sites: tuple[str, ...] = ()) -> list[SearchResult]:
    if engine == "duckduckgo":
        return _search_ddgs(query, limit, config)
    if engine == "brave":
        return _search_ddgs(query, limit, config, backend="brave")
    if engine == "google":
        return _search_ddgs(query, limit, config, backend="google")
    if engine == "bing":
        return _search_ddgs(query, limit, config, backend="bing")
    if engine == "yahoo":
        return _search_ddgs(query, limit, config, backend="yahoo")
    if engine == "exa":
        return _search_exa(query, limit, config)
    if engine == "tavily":
        return _search_tavily(query, limit, config)
    if engine == "perplexity":
        return _search_perplexity(query, limit, config)
    if engine == "firecrawl":
        return _search_firecrawl(query, limit, config)
    if engine == "serpapi":
        return _search_serpapi(query, limit, config)
    if engine == "linkup":
        return _search_linkup(query, limit, config)
    if engine == "jina":
        return _search_jina(query, limit, config, sites)
    raise ValueError(f"Unknown engine: {engine}")


def _search_ddgs(
    query: str, limit: int, config: AppConfig, backend: str = "duckduckgo"
) -> list[SearchResult]:
    with DDGS(proxy=None, timeout=config.search.timeout) as client:
        raw = client.text(
            query,
            safesearch=config.search.safe_search,
            max_results=limit,
            backend=backend,
        )
    return normalize_results(raw, backend)


def _search_exa(query: str, limit: int, config: AppConfig) -> list[SearchResult]:
    if not _EXA_AVAILABLE:
        raise ImportError("exa-py is not available. Please ensure drupal-web-search is installed correctly.")
    api_key = config.engines.get("exa", EngineSettings(name="exa", enabled=False)).api_key
    if not api_key:
        raise ValueError("EXA_API_KEY is required for the exa engine. Add it to config.toml or set the environment variable.")
    client = Exa(api_key)
    results = client.search(query, num_results=limit)
    return [
        SearchResult(
            title=r.title or r.url,
            url=r.url,
            snippet=" ".join(r.highlights) if r.highlights else "",
            engine="exa",
        )
        for r in results.results
    ]


def _search_tavily(query: str, limit: int, config: AppConfig) -> list[SearchResult]:
    if not _TAVILY_AVAILABLE:
        raise ImportError("tavily-python is not available. Please ensure drupal-web-search is installed correctly.")
    api_key = config.engines.get("tavily", EngineSettings(name="tavily", enabled=False)).api_key
    if not api_key:
        raise ValueError("TAVILY_API_KEY is required for the tavily engine. Add it to config.toml or set the environment variable.")
    client = TavilyClient(api_key=api_key)
    response = client.search(query, max_results=limit)
    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            snippet=r.get("content", ""),
            engine="tavily",
        )
        for r in response.get("results", [])
    ]


def _search_perplexity(query: str, limit: int, config: AppConfig) -> list[SearchResult]:
    if not _PERPLEXITY_AVAILABLE:
        raise ImportError("perplexity is not available. Please ensure drupal-web-search is installed correctly.")
    api_key = config.engines.get(
        "perplexity", EngineSettings(name="perplexity", enabled=False)
    ).api_key
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY is required for the perplexity engine. Add it to config.toml or set the environment variable.")
    client = perplexity.Perplexity(api_key=api_key)
    response = client.search.create(query=query, max_results=limit)
    return [
        SearchResult(
            title=r.title,
            url=r.url,
            snippet=r.snippet,
            engine="perplexity",
        )
        for r in response.results
    ]


def _search_firecrawl(query: str, limit: int, config: AppConfig) -> list[SearchResult]:
    if not _FIRECRAWL_AVAILABLE:
        raise ImportError("firecrawl-py is not available. Please ensure drupal-web-search is installed correctly.")
    api_key = config.engines.get(
        "firecrawl", EngineSettings(name="firecrawl", enabled=False)
    ).api_key
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY is required for the firecrawl engine. Add it to config.toml or set the environment variable.")
    client = firecrawl.FirecrawlApp(api_key=api_key)
    resp = client.search(query, limit=limit)
    results = resp.get("data", []) if isinstance(resp, dict) else []
    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            snippet=r.get("description", ""),
            engine="firecrawl",
        )
        for r in results
    ]


def _search_serpapi(query: str, limit: int, config: AppConfig) -> list[SearchResult]:
    if not _SERPAPI_AVAILABLE:
        raise ImportError("serpapi is not available. Please ensure drupal-web-search is installed correctly.")
    api_key = config.engines.get("serpapi", EngineSettings(name="serpapi", enabled=False)).api_key
    if not api_key:
        raise ValueError("SERPAPI_API_KEY is required for the serpapi engine. Add it to config.toml or set the environment variable.")
    client = serpapi.SerpAPIClient(api_key=api_key)
    resp = client.search({"q": query, "num": limit})
    results = resp.get("organic_results", [])
    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("link", ""),
            snippet=r.get("snippet", ""),
            engine="serpapi",
        )
        for r in results
    ]


def _search_linkup(query: str, limit: int, config: AppConfig) -> list[SearchResult]:
    if not _LINKUP_AVAILABLE:
        raise ImportError("linkup-sdk is not available. Please ensure drupal-web-search is installed correctly.")
    api_key = config.engines.get("linkup", EngineSettings(name="linkup", enabled=False)).api_key
    if not api_key:
        raise ValueError("LINKUP_API_KEY is required for the linkup engine. Add it to config.toml or set the environment variable.")
    client = LinkupClient(api_key=api_key)
    include_domains = list(config.site_preferences.restrict_to) if config.site_preferences.restrict_to else None
    response = client.search(
        query=query,
        depth="standard",
        output_type="searchResults",
        include_images=False,
        include_domains=include_domains,
        max_results=limit,
    )
    return [
        SearchResult(
            title=r.name or r.url,
            url=r.url,
            snippet=r.content or "",
            engine="linkup",
        )
        for r in response.results
    ]


def _search_jina(query: str, limit: int, config: AppConfig, sites: tuple[str, ...] = ()) -> list[SearchResult]:
    if not _JINA_AVAILABLE:
        raise ImportError("httpx is required for jina engine. Please ensure drupal-web-search is installed correctly.")
    api_key = config.engines.get("jina", EngineSettings(name="jina", enabled=False)).api_key
    if not api_key:
        raise ValueError("JINA_API_KEY is required for the jina engine. Add it to config.toml or set the environment variable.")
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    params: dict[str, str | int] = {"q": query, "num": limit}
    if sites:
        params["site"] = sites[0]
    response = httpx.get(
        "https://s.jina.ai/",
        params=params,
        headers=headers,
        timeout=config.search.timeout,
    )
    data = response.json()
    results = data.get("data", []) if isinstance(data.get("data"), list) else []
    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            snippet=r.get("description", ""),
            engine="jina",
        )
        for r in results
    ]


def apply_site_preferences(results: list[SearchResult], config: AppConfig) -> list[SearchResult]:
    filtered_results = [
        result
        for result in results
        if not domain_matches(extract_domain(result.url), config.site_preferences.blocked)
    ]

    seen_urls: set[str] = set()
    deduplicated_results: list[SearchResult] = []
    for result in filtered_results:
        if result.url in seen_urls:
            continue
        seen_urls.add(result.url)
        deduplicated_results.append(result)

    return sorted(
        deduplicated_results,
        key=lambda result: (
            not domain_matches(extract_domain(result.url), config.site_preferences.preferred),
            result.title.lower(),
        ),
    )


def search_web(
    query: str,
    config: AppConfig,
    requested_engine: str | None = None,
    limit: int | None = None,
    site: str | None = None,
) -> list[SearchResult]:
    engine_order = build_engine_order(config, requested_engine=requested_engine)
    result_limit = limit or config.search.num_results

    cli_sites = site if site else []
    config_sites = config.site_preferences.restrict_to
    all_sites = tuple(s for s in cli_sites) + config_sites

    last_error: Exception | None = None
    engines_with_native_site = {"jina", "linkup"}
    engines_without_prefixed_site_support = {"duckduckgo", "google", "yahoo"}
    for engine in engine_order:
        modified_query = query
        if all_sites and engine not in engines_with_native_site and engine not in engines_without_prefixed_site_support:
            site_prefix = " ".join(f"site:{s}" for s in all_sites)
            modified_query = f"{site_prefix} {query}"
        try:
            raw_results = _run_engine(engine, modified_query, result_limit, config, all_sites)
        except Exception as exc:  # pragma: no cover - network/runtime failure path
            last_error = exc
            continue

        ranked_results = apply_site_preferences(raw_results, config)
        if ranked_results:
            return ranked_results[:result_limit]

    if last_error is not None:
        if requested_engine:
            raise RuntimeError(f"Engine '{requested_engine}' failed: {last_error}") from last_error
        raise RuntimeError(
            f"Search failed for all configured engines: {last_error}"
        ) from last_error

    return []


def results_to_dicts(results: list[SearchResult]) -> list[dict[str, str]]:
    return [asdict(result) for result in results]
