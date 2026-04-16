# Drupal News Aggregator - Usage Guide

## Basic Usage

### 1. Full Pipeline (Fetch + AI + Email)
```bash
# News report with Anthropic
./index.py --provider anthropic

# Binews report with OpenAI
./index.py --provider openai --days 14

# Monthly report without email
./index.py --provider gemini --days 30 --email no
```

## Separate Fetch and Summarize

### 2. Fetch Sources Only (No AI)
```bash
# Collect sources for today (7 days by default)
./index.py --fetch-only

# Collect sources for 14 days
./index.py --fetch-only --days 14
```

This creates:
- `runs/2025-10-25/sources.json` - Raw data
- `runs/2025-10-25/parsed.md` - Human-readable list
- `runs/2025-10-25/validation_report.json` - Validation results

### 3. Use Cached Sources with Different AI Models
```bash
# Try different AI providers on the same data
./index.py --use-sources 2025-10-25 --provider anthropic --email no
./index.py --use-sources 2025-10-25 --provider openai --email no
./index.py --use-sources 2025-10-25 --provider gemini --email no

# Send email with specific provider
./index.py --use-sources 2025-10-25 --provider anthropic --email yes
```

**Benefits:**
- ✅ No re-fetching RSS feeds (saves time)
- ✅ Test different AI models on same data
- ✅ Consistent input for comparison
- ✅ Faster iteration

## Workflow Examples

### Example 1: Morning Collection, Afternoon Summary
```bash
# Morning: Collect sources (fast)
./index.py --fetch-only --days 7

# Afternoon: Generate summary with preferred AI
./index.py --use-sources 2025-10-25 --provider anthropic
```

### Example 2: Test Multiple AI Models
```bash
# Collect once
./index.py --fetch-only --days 14

# Compare different models
./index.py --use-sources 2025-10-25 --provider anthropic --email no
./index.py --use-sources 2025-10-25 --provider openai --email no
./index.py --use-sources 2025-10-25 --provider gemini --email no

# Review summaries and pick the best one
# Send email with the best result (files are already there)
./send_email.py 2025-10-25 --days 14
```

### Example 3: Re-generate with Different Model
```bash
# Already ran with one provider but want to try another
./index.py --use-sources 2025-10-25 --provider gemini --email yes
```

## Send Email from Existing Run

### 4. Send Email Later
```bash
# Send email from latest run
./send_email.py --latest --days 7

# Send email from specific date
./send_email.py 2025-10-25 --days 14

# Send to different recipient
./send_email.py 2025-10-25 --to someone@example.com --days 7
```

## Available Providers

Configure providers in `providers.yaml`:
- `anthropic`   - Claude models (fast, good quality)
- `openai`      - GPT models (versatile)
- `gemini`      - Google Gemini (multimodal)
- `ollama`      - Local models (private, free)
- `qwen`        - Qwen models
- `grok`        - xAI Grok
- `deepseek`    - DeepSeek models
- `openrouter`  - OpenRouter aggregator

## File Structure

```
runs/
  2025-10-25/
    sources.json     # Raw collected data (reusable)
    parsed.md        # Human-readable list
    validation_report.json
    summary.md       # AI-generated summary
    summary.pdf      # PDF version
    email.txt        # Email log
    metrics.json     # Performance metrics
    run.log          # Execution log
```

## Tips

1. **Fetch Once, Summarize Many**: Use `--fetch-only` in the morning, then try different AI models throughout the day
2. **Compare Models**: Generate summaries with multiple providers from the same sources to compare quality
3. **Save Time**: Skip re-fetching when experimenting with prompts or models
4. **Cost Control**: Use cached sources to avoid redundant API calls to feed sources

## Cron Automation

Schedule a news summary every Monday at 07:00 local time:

```
0 7 * * MON /usr/bin/env bash -lc 'cd /srv/Samsung4T/Tools/AI/drupal_news/claude && source venv/bin/activate && PYTHONPATH=src python index.py --provider anthropic --email yes'
```

Adjust the schedule, provider, and email flag as needed for your environment.
