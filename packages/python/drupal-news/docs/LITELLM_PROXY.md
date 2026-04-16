# LiteLLM Proxy Configuration

[LiteLLM](https://docs.litellm.ai) is a unified interface to 100+ LLMs with built-in load balancing, fallbacks, and cost tracking.

## Overview

LiteLLM provides:
- Single API for all major providers
- Load balancing across multiple API keys
- Automatic fallbacks
- Cost tracking and analytics
- Rate limiting
- Caching (with Redis)

## Quick Setup

### Step 1: Install LiteLLM

```bash
# Install LiteLLM with proxy support
pip install litellm[proxy]
```

### Step 2: Create LiteLLM Configuration

Create `litellm_config.yaml`:

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY

  - model_name: claude-3-5-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: grok-beta
    litellm_params:
      model: xai/grok-beta
      api_key: os.environ/GROK_API_KEY
```

### Step 3: Start LiteLLM Proxy Server

```bash
# Start proxy server (default port 4000)
litellm --config litellm_config.yaml
```

### Step 4: Configure Drupal Aggregator

Update `providers.yaml` to use LiteLLM:

```yaml
# providers.yaml - Use LiteLLM for all providers
providers:
  openai:
    client: openai_client
    model: gpt-4  # Model name from litellm_config.yaml
    temperature: 0.2
    api_url: http://localhost:4000  # LiteLLM default port

  anthropic:
    client: openai_client  # LiteLLM is OpenAI-compatible
    model: claude-3-5-sonnet
    temperature: 0.2
    api_url: http://localhost:4000

  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2
    api_url: http://localhost:4000
```

### Step 5: Run Normally

```bash
./index.py --provider openai --days 7
```

## Advanced Features

### Load Balancing

Automatically rotate between multiple API keys:

```yaml
# In LiteLLM config
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY_1

  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY_2  # Automatic rotation
```

### Cost Tracking

Add custom headers for cost tracking:

```yaml
# providers.yaml
openai:
  api_url: http://localhost:4000
  headers:
    user: drupal-aggregator
    tags: news-report
```

### Authentication

If LiteLLM proxy has authentication enabled:

```yaml
openai:
  api_url: http://localhost:4000
  headers:
    Authorization: Bearer your-litellm-master-key
```

### Custom Headers

Pass any custom headers through LiteLLM:

```yaml
openai:
  api_url: http://localhost:4000
  headers:
    Custom-Header: value
    Another-Header: another-value
```

## Supported Providers

LiteLLM works with:
- ✅ **openai** - Via OpenAI-compatible endpoint
- ✅ **anthropic** - Via OpenAI-compatible endpoint
- ✅ **grok** - Via OpenAI-compatible endpoint
- ✅ **gemini** - Via OpenAI-compatible endpoint
- ✅ **ollama** - Via OpenAI-compatible endpoint

## Testing

Test your LiteLLM configuration:

```bash
# Verify LiteLLM is running
curl http://localhost:4000/health

# Test with Drupal Aggregator
./index.py --provider openai --dry-run
./index.py --provider openai --use-sources 2025-10-25 --email no
```

## Troubleshooting

### Connection Issues

1. Verify LiteLLM proxy is running:
   ```bash
   curl http://localhost:4000/health
   ```

2. Check LiteLLM logs for errors

3. Ensure model names match between `litellm_config.yaml` and `providers.yaml`

### Model Not Found

1. Verify model names in `litellm_config.yaml` match those used in `providers.yaml`
2. Check API keys are set in environment variables
3. Restart LiteLLM after configuration changes

### Performance Issues

- Consider using Redis for caching
- Enable load balancing for better throughput
- Monitor LiteLLM metrics

## Quick Start Example

The repository includes ready-to-use configuration examples:

```bash
# For LiteLLM
cp litellm_config.example.yaml litellm_config.yaml
cp providers.litellm.example.yaml providers.yaml
litellm --config litellm_config.yaml
```

## Comparison: Portkey vs LiteLLM

| Feature | Portkey | LiteLLM |
|---------|---------|---------|
| **Hosting** | Cloud (SaaS) | Self-hosted |
| **Setup** | API keys only | Requires local server |
| **UI Dashboard** | ✅ Full web UI | ⚠️ Limited |
| **Cost** | Paid (free tier) | Free (open source) |
| **Load Balancing** | ✅ Yes | ✅ Yes |
| **Fallbacks** | ✅ Yes | ✅ Yes |
| **Caching** | ✅ Yes | ✅ Yes (Redis) |
| **Analytics** | ✅ Built-in | ⚠️ Via integrations |
| **Rate Limiting** | ✅ Yes | ✅ Yes (Redis) |
| **Best For** | Quick setup, monitoring | Full control, privacy |

## See Also

- [LiteLLM Documentation](https://docs.litellm.ai)
- [Portkey Proxy Guide](PORTKEY_PROXY.md)
- [Generic Provider Guide](GENERIC_PROVIDER.md)
- [Proxy Quick Start](PROXY_QUICKSTART.md)