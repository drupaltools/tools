# Drupal Web Search

Generic web search CLI with DDGS (free), Exa, Tavily, Perplexity, Firecrawl, and SerpAPI - configurable engines, fallback order, and site preferences.

## Setup

```bash
cd packages/python/drupal-web-search
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]          # core + dev tools
pip install -e .[premium]      # add Exa + Tavily + Perplexity + Firecrawl + SerpAPI
cp .env.example .env
cp config.toml config.local.toml
```

## Usage

```bash
drupal-web-search "drupal cache tags"
drupal-web-search "drupal cache tags" --engine brave --limit 5
drupal-web-search "drupal cache tags" --engine exa --limit 5
drupal-web-search "drupal cache tags" --engine tavily
drupal-web-search "drupal cache tags" --engine perplexity
drupal-web-search "drupal cache tags" --json
drupal-web-search "drupal cache tags" --verbose

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

| Engine         | Install extra  | API key required | Notes                               |
| -------------- | -------------- | ---------------- | ----------------------------------- |
| duckduckgo     | (built-in)     | No               | Free, default fallback              |
| brave          | (built-in)     | Optional\*       | Higher quality, $5/mo free credit\* |
| google         | (built-in)     | No               | DDGS backend (not Google's API)     |
| bing           | (built-in)     | No               | DDGS backend (not Bing's API)       |
| **exa**        | `[exa]`        | Yes              | Code-aware semantic search          |
| **tavily**     | `[tavily]`     | Yes              | LLM-optimized, 1K credits/mo free   |
| **perplexity** | `[perplexity]` | Yes              | Conversational, up-to-date          |
| **firecrawl**  | `[firecrawl]`  | Yes              | Scraping + search, 500 credits/mo   |
| **serpapi**    | `[serpapi]`    | Yes              | 15+ engines via SerpAPI, ~$7.25/1K  |

\*Brave: no longer free for new signups. $5/mo with $5 free credit. Existing free-plan users keep 2,000 req/month.

### Get API keys

| Engine     | Sign up / key page                              |
| ---------- | ----------------------------------------------- |
| brave      | https://api-dashboard.search.brave.com/register |
| exa        | https://dashboard.exa.ai/onboarding             |
| tavily     | https://tavily.com                              |
| perplexity | https://api.perplexity.ai/api-keys              |
| firecrawl  | https://firecrawl.dev/app/api-keys              |
| serpapi    | https://serpapi.com/users/sign_up               |

Premium engines are disabled by default. Enable in `config.toml`:

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
