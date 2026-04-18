# Drupal Web Search

Generic web search CLI with DDGS (free), Exa, Tavily, Perplexity, Firecrawl, and SerpAPI - configurable engines, fallback order, and site preferences.

## Setup

```bash
cd packages/python/drupal-web-search
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]   # core + dev tools (or just pip install -e . for core only)
cp .env.example .env
cp config.toml config.local.toml
```

## Usage

```bash
# Activate virtual environment first
source venv/bin/activate

# Then run (or use .venv/bin/drupal-web-search directly without activating)
drupal-web-search "drupal cache tags"
drupal-web-search "drupal cache tags" --engine brave --limit 5
drupal-web-search "drupal cache tags" --engine exa --limit 5
drupal-web-search "drupal cache tags" --engine tavily
drupal-web-search "drupal cache tags" --engine perplexity
drupal-web-search "drupal cache tags" --json
drupal-web-search "drupal cache tags" --verbose

# Or run directly without activating
.venv/bin/drupal-web-search "drupal cache tags" --engine exa
.venv/bin/python -m drupal_web_search "drupal cache tags" --engine exa

# Restrict to specific domain(s)
drupal-web-search "cache tags" --site drupal.org
drupal-web-search "cache tags" --site drupal.org --site drupalproject.org
```

### Site preferences via config

```toml
# config.toml
[site_preferences]
restrict_to = ["drupal.org", "drupalproject.org"]  # engine only returns results from these domains
preferred = ["github.com"]                            # these domains bubble to top of results
blocked = ["spam-site.com"]                           # these domains are removed from results
```

CLI `--site` flags are combined with `restrict_to` and prepended to every query as `site:drupal.org site:drupalproject.org <query>`.

## Engines

| Engine         | API key required | Notes                               |
| -------------- | ---------------- | ----------------------------------- |
| duckduckgo     | No               | Free, default fallback              |
| google         | No               | DDGS backend (not Google's API)     |
| bing           | No               | DDGS backend (not Bing's API)       |
| yahoo          | No               | DDGS backend (not Yahoo's API)      |
| brave          | Yes              | Higher quality, $5/mo free credit   |
| exa            | Yes              | Code-aware semantic search          |
| tavily         | Yes              | LLM-optimized, 1K credits/mo free   |
| perplexity     | Yes              | Conversational, up-to-date          |
| firecrawl      | Yes              | Scraping + search, 500 credits/mo   |
| serpapi        | Yes              | 15+ engines via SerpAPI, ~$7.25/1K  |
| linkup         | Yes              | Fast search, free tier available    |
| jina           | Yes              | LLM-friendly, 100 RPM free tier     |

### Engine limitations

The DDGS-based engines (duckduckgo, google, bing, yahoo) share a common underlying library but have inconsistent behavior:

- **duckduckgo**: Works reliably for general searches.
- **bing**: Supports `site:` query operators for domain filtering.
- **google**, **yahoo**: Often fail with "No results found" or request errors in some environments. These are disabled in the default fallback order.
- **site: operators**: Not supported by duckduckgo/google/yahoo backends. Only `bing` properly handles query-level site restrictions.

Workaround: Configure `bing` explicitly when you need site filtering, or use engines with native site support (`jina`, `linkup`).

### Get API keys

| Engine     | Sign up / key page                              |
| ---------- | ----------------------------------------------- |
| brave      | https://api-dashboard.search.brave.com/register |
| exa        | https://dashboard.exa.ai/api-keys               |
| tavily     | https://app.tavily.com/home                     |
| perplexity | https://www.perplexity.ai/account/api/keys      |
| firecrawl  | https://firecrawl.dev/app/api-keys              |
| serpapi    | https://serpapi.com/manage-api-key              |
| linkup     | https://app.linkup.so/api-keys                  |
| jina       | https://jina.ai/api-dashboard/key-manager       |

All engines are installed by default. Engines requiring API keys are disabled until configured in `config.toml`:

```toml
[engines]
default = "duckduckgo"
fallback_order = ["exa", "tavily"]

[engines.exa]
api_key = "${EXA_API_KEY}"
enabled = true
```

## Config

`config.toml` controls default engine, fallback order, search defaults, and site preferences (`restrict_to`, `preferred`, `blocked`).

Environment variables can be referenced with `${VAR_NAME}` values inside `config.toml`.

## Output

Each result includes:

- title
- url
- snippet
- engine

## Similar tools

- [@plust/search-sdk](https://github.com/PlustOrg/search-sdk) - TypeScript SDK (unified interface for Google, SerpAPI, Brave, Exa, Tavily, SearXNG, Arxiv, DuckDuckGo)
- [ddgs](https://github.com/deedy5/ddgs) - Python metasearch library (used as the backend for duckduckgo, brave, google, bing, yahoo)
- [wizsearch](https://github.com/mirasoth/wizsearch) - Python web search library with multiple engine support
