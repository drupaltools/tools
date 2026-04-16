# Drupal News Aggregator

Automated Drupal news aggregation with AI summarization.

## Installation

### From PyPI

```bash
pip install drupal-news

# With AI providers
pip install "drupal-news[openai]"
pip install "drupal-news[anthropic]"
pip install "drupal-news[all-providers]"
```

### From Source

```bash
./setup.sh
source venv/bin/activate
```

## Quick Start

```bash
# Using installed package
drupal-news --dry-run

# Or from source
python3 index.py --dry-run
```

## Configuration

### Unified Configuration (config.yml)

All configuration is now in a single `config.yml` file:

```bash
# Create from example
cp config.example.yml config.yml

# Edit to customize
nano config.yml
```

**Configuration sections:**

- **Core settings**: timeframe, HTTP options, email, markdown
- **Sources**: RSS feeds and web pages to scrape
- **AI providers**: Model configurations for summarization
- **Prompt template**: Customize AI summarization instructions
- **API keys**: Store or reference environment variables

### Custom Configuration Path

```bash
drupal-news --config /path/to/config.yml

# Or from source
python3 index.py --config /path/to/config.yml
```

### Environment Variables (.env)

You can still use `.env` for sensitive data:

```bash
# .env (optional)
OPENROUTER_API_KEY=sk-or-v1-...
ANTHROPIC_API_KEY=sk-ant-api03-...
TIMEZONE=Europe/Athens
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASS=password
MAIL_TO=recipient@example.com
MAIL_FROM=sender@example.com
```

Reference them in `config.yml` using `${VAR_NAME}`:

```yaml
api_keys:
  OPENROUTER_API_KEY: ${OPENROUTER_API_KEY}  # From .env
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
```

### Configuration Examples

See `config.example.yml` for comprehensive examples of:

- Multiple AI providers (OpenAI, Anthropic, Gemini, Ollama, etc.)
- Custom API endpoints and proxies
- Advanced page scraping with CSS selectors
- Custom prompt templates

**Migration Guide**: See `MIGRATION.md` if upgrading from old config files

## Usage

### Main Aggregator

```bash
# Using installed package
drupal-news --provider openai --days 7
drupal-news --dry-run --verbose
drupal-news --provider anthropic --email yes

# Or from source
python3 index.py --provider openai --days 7
```

### Scheduler

```bash
# Using installed package
drupal-news-scheduler --every friday --hour 9 --provider openai
drupal-news-scheduler --every monday --hour 8 --email yes --days 7

# Or from source
python3 scheduler.py --every friday --hour 9 --provider openai
```

### Email Sender

```bash
# Using installed package
drupal-news-email --latest
drupal-news-email --run-dir runs/2025-10-29

# Or from source
python3 -m drupal_news.email_sender --latest
```

### Cron

```bash
# Using installed package
0 9 * * 5 drupal-news --provider openai --email yes

# Or from source
0 9 * * 5 cd /path && python3 index.py --provider openai
```

## Web Viewer

```bash
# Using installed package
drupal-news-viewer
# Open http://localhost:5000

# Or from source
python3 src/viewer.py
```

Features: tabs/split view, run history, metrics, logs

## Providers

Built-in: OpenAI, Anthropic, Gemini, Ollama, LMStudio, Qwen, Grok, DeepSeek, OpenRouter

**Generic:** Works with ANY OpenAI-compatible API (OpenRouter, Together AI, Groq, Perplexity, Fireworks, Azure OpenAI, custom endpoints)

See: [Generic Provider Guide](docs/GENERIC_PROVIDER.md)

## CLI Commands

### drupal-news

Main aggregator command. Fetches, parses, and summarizes Drupal news.

```bash
drupal-news [OPTIONS]

Options:
  --provider <name>       AI provider (openai, anthropic, gemini, etc.)
  --model <name>          Override provider's default model
  --days <n>              Timeframe in days (default: 7)
  --email yes|no          Send email report
  --dry-run               Skip AI and email (testing mode)
  --fetch-only            Only fetch and parse, skip AI
  --use-sources <date>    Use cached sources from date (YYYY-MM-DD)
  --config <path>         Custom config.yml path
  --env <path>            Custom .env path
  --outdir <path>         Custom output directory
  --verbose               Enable debug logging
```

### drupal-news-scheduler

Schedule recurring aggregator runs.

```bash
drupal-news-scheduler --every <day> [OPTIONS]

Options:
  --every <day>           Day of week (monday-sunday)
  --hour <n>              Hour to run (0-23, default: 9)
  --minute <n>            Minute to run (0-59, default: 0)
  --provider <name>       AI provider to use
  --model <name>          Model override
  --email yes|no          Send email
  --days <n>              Number of days to aggregate
```

### drupal-news-email

Send aggregated reports via email.

```bash
drupal-news-email [OPTIONS]

Options:
  --latest                Send latest report
  --run-dir <path>        Send specific run directory
  --days <n>              Days back to check (default: 7)
```

### drupal-news-viewer

Launch web interface to view reports.

```bash
drupal-news-viewer

Opens http://localhost:5000
Features: tabs, run history, metrics, logs
```

## Output

`runs/YYYY-MM-DD/`: parsed.md, summary.md, sources.json, metrics.json, run.log

## Project Structure

When using from PyPI, configuration files are in `~/.drupal-news/` or current directory.

When using from source:

```
├── setup.sh        # Setup script
├── index.py        # Main entry (wrapper)
├── scheduler.py    # Scheduler (wrapper)
├── src/            # Source code
├── src/viewer.py        # Web viewer (wrapper)
├── venv/                # Virtual env
├── config.yml           # Unified configuration
├── config.example.yml   # Configuration examples
└── .env                 # Optional environment variables
```

## Exit Codes

- 0:  Success
- 10: Partial fetch failure
- 20: Validation failed
- 30: Summarizer failed
- 40: Email failure
- 50: Integrity check failed

## Contributing

Contributions welcome! See [docs/RELEASING.md](docs/RELEASING.md) for release process.

### Creating a Release

```bash
# Patch release (bug fixes)
./release.sh patch -m "Bug fixes and improvements"

# Minor release (new features)
./release.sh minor -m "New features" --push

# Major release (breaking changes)
./release.sh major -m "Breaking changes" --push
```

The release script:

- Updates VERSION file
- Updates RELEASES.md with changelog
- Creates git commit and tag
- Optionally pushes to trigger automated PyPI publishing

## License

[GPL-V2](LICENSE.txt)
