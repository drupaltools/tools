# Portkey Proxy Configuration

[Portkey](https://portkey.ai) provides AI gateway features like caching, fallbacks, and monitoring for the Drupal News Aggregator.

## Overview

Portkey acts as a proxy between your application and AI providers, offering:
- Request caching
- Automatic fallbacks
- Usage monitoring and analytics
- Rate limiting
- Cost tracking

## Quick Setup

### Step 1: Get Portkey Keys

1. Sign up at https://portkey.ai
2. Create an API key
3. Create a virtual key for your AI provider (e.g., Grok, OpenAI, Anthropic)

### Step 2: Configure providers.yaml

```yaml
providers:
  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2
    api_url: https://api.portkey.ai/v1
    headers:
      x-portkey-api-key: pk-***YOUR_PORTKEY_API_KEY***
      x-portkey-virtual-key: vk-***YOUR_GROK_VIRTUAL_KEY***
```

### Step 3: Keep Provider API Key

Still set your provider API key in `.env` - Portkey will use it via the virtual key:

```bash
GROK_API_KEY=xai-***YOUR_GROK_API_KEY***
```

### Step 4: Run Normally

```bash
./index.py --provider grok --days 7
```

## Advanced Features

### Request Tracing

Add trace IDs and metadata for better monitoring:

```yaml
grok:
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: pk-***
    x-portkey-virtual-key: vk-***
    x-portkey-trace-id: drupal-news-{date}
    x-portkey-metadata: '{"source":"drupal-aggregator"}'
```

### Cache Control

Force cache refresh when needed:

```yaml
grok:
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: pk-***
    x-portkey-virtual-key: vk-***
    x-portkey-cache-force-refresh: "true"
```

### Fallback Configuration

Use pre-configured fallback chains:

```yaml
grok:
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: pk-***
    x-portkey-config: config-id-with-fallbacks
```

## Environment Variables

Use environment variables for better security:

```yaml
grok:
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: ${PORTKEY_API_KEY}
    x-portkey-virtual-key: ${PORTKEY_GROK_KEY}
```

Then in `.env`:
```bash
PORTKEY_API_KEY=pk-***
PORTKEY_GROK_KEY=vk-***
```

## Supported Providers

Portkey works with:
- ✅ **grok** - Full support
- ✅ **openai** - Via custom endpoint
- ✅ **anthropic** - Via proxy
- ✅ **openrouter** - Via Portkey

## Testing

Test your Portkey configuration:

```bash
# Dry run to verify config loads
./index.py --provider grok --dry-run

# Full run with Portkey
./index.py --provider grok --use-sources 2025-10-25 --email no
```

## Troubleshooting

### Authentication Errors

1. Verify your API keys in `.env`
2. Check Portkey virtual key is correct
3. Ensure headers are formatted correctly

### Timeout Issues

Increase timeout if using slow proxies:

```python
# In provider client:
timeout=300.0  # 5 minutes
```

## Security Notes

- Never commit API keys to git
- Use `.env` for secrets
- Consider using environment variables for Portkey keys
- Rotate keys regularly
- Monitor usage through Portkey dashboard

## Quick Start Example

The repository includes a ready-to-use configuration example:

```bash
cp providers.portkey.example.yaml providers.yaml
# Edit providers.yaml with your Portkey keys
```

## See Also

- [Portkey Documentation](https://docs.portkey.ai)
- [Generic Provider Guide](GENERIC_PROVIDER.md)
- [Proxy Quick Start](PROXY_QUICKSTART.md)