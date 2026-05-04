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
| openai | https://platform.openai.com/account/api-keys  |
| claude | https://www.anthropic.com/account/api     |
| gemini_search | https://aistudio.google.com/app/apikey      |
| grok_search  | https://console.x.ai/                       |
| openrouter  | https://openrouter.ai/keys                  |

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
- [openrouter SDK web-search](https://openrouter.ai/docs/guides/features/server-tools/web-search)
- [ddgs](https://github.com/deedy5/ddgs) - Python metasearch library (used as the backend for duckduckgo, brave, google, bing, yahoo)
- [wizsearch](https://github.com/mirasoth/wizsearch) - Python web search library with multiple engine support

## Alternative Libraries

Option A — Python (DDGS) ← simplest, most practical

Free, zero API keys needed for most engines

```bash
pip install ddgs
```

```python
from ddgs import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text("query", max_results=10))
```

9 engines: DuckDuckGo, Brave, Google, Bing, Yandex, Yahoo, Wikipedia, Mojeek, Gropipedia

Option B — Python (WizSearch) ← closer to PlustOrg model

```bash
pip install wizsearch
```

```python
from wizsearch import WizSearch, WizSearchConfig

config = WizSearchConfig(enabled_engines=["duckduckgo", "brave", "tavily"])
results = WizSearch(config).search("query")
```

9 engines: DuckDuckGo, Tavily, Brave, Google, Bing, SearXNG, Baidu, Google AI, WeChat

Option C — TypeScript (@plust/search-sdk) ← closest to your reference

```bash
npm install @plust/search-sdk
```

```typescript
import { google, webSearch } from '@plust/search-sdk';

const results = await webSearch({ query, provider: [google.configure({apiKey, cx})] });
```

9 engines: Google, SerpAPI, Brave, Exa, Tavily, SearXNG, Arxiv, DuckDuckGo, Perplexity
