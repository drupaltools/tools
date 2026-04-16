# Custom API URLs and Proxy Configuration

This document explains how to use custom API endpoints and proxy services with the Drupal News Aggregator.

## Overview

You can configure custom API URLs and headers for any provider in `providers.yaml`. This is useful for:

- Using proxy services (Portkey, LiteLLM, etc.)
- Custom deployments
- Load balancers
- Local development endpoints
- Rate limiting management
- Cost tracking and monitoring

## Basic Configuration

Add `api_url` and optionally `headers` to any provider in `providers.yaml`:

```yaml
providers:
  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2
    api_url: https://your-custom-url.com/v1
    headers:
      Custom-Header: value
      Another-Header: another-value
```

## Proxy Services

### Portkey Proxy

[Portkey](https://portkey.ai) provides AI gateway features like caching, fallbacks, and monitoring.

**See:** [Portkey Proxy Guide](PORTKEY_PROXY.md) for complete setup instructions.

### LiteLLM Proxy

[LiteLLM](https://docs.litellm.ai) is a unified interface to 100+ LLMs with built-in load balancing, fallbacks, and cost tracking.

**See:** [LiteLLM Proxy Guide](LITELLM_PROXY.md) for complete setup instructions.

### Generic Provider

For maximum flexibility, use the **generic provider** which works with ANY OpenAI-compatible API.

**See:** [Generic Provider Quick Start](GENERIC_PROVIDER_QUICKSTART.md) for quick setup.

## Local Endpoints

### Ollama (Custom Port)

```yaml
ollama:
  client: ollama_client
  model: qwen2.5:7b-instruct
  api_url: http://192.168.1.100:11434
```

### LM Studio (Custom Port)

```yaml
lmstudio:
  client: lmstudio_client
  model: your-model
  api_url: http://localhost:1234
```

## Environment Variables

You can use environment variables in headers:

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

## Anthropic-Compatible Providers

### z.ai (GLM-4.6)

```yaml
zai:
  client: anthropic_client
  model: glm-4.6
  temperature: 0.2
  api_url: https://api.z.ai/api/anthropic
```

Required environment variable:
```bash
ZAI_API_KEY=your_zai_api_key
```

**Usage:**
```bash
drupal-news --provider zai
```

### MiniMax (MiniMax-M2)

```yaml
minimax:
  client: anthropic_client
  model: minimax-m2
  temperature: 0.2
  api_url: https://api.minimax.io/anthropic
```

Required environment variable:
```bash
MINIMAX_API_KEY=your_minimax_api_key
```

**Usage:**
```bash
drupal-news --provider minimax
```

Both providers use the Anthropic API format and are configured in `config.yml` by default.

## Supported Providers

Custom URLs and headers work with:
- ✅ **grok** - Full support
- ✅ **openai** - Via custom endpoint
- ✅ **anthropic** - Via proxy
- ✅ **ollama** - Custom host/port
- ✅ **openrouter** - Via Portkey
- ✅ **zai** - GLM-4.6 via Anthropic-compatible endpoint
- ✅ **minimax** - MiniMax-M2 via Anthropic-compatible endpoint
- ⚠️ **gemini** - Limited (uses official SDK)

## Testing

Test your configuration:

```bash
# Dry run to verify config loads
./index.py --provider grok --dry-run

# Fetch-only (no API calls)
./index.py --fetch-only

# Full run with custom endpoint
./index.py --provider grok --use-sources 2025-10-25 --email no
```

## Quick Start Examples

The repository includes ready-to-use configuration examples:

- `providers.generic.example.yaml` - Generic provider for any service
- `providers.portkey.example.yaml` - Portkey proxy configuration
- `providers.litellm.example.yaml` - LiteLLM proxy configuration
- `litellm_config.example.yaml` - LiteLLM server configuration

Copy and customize these files for your setup:

```bash
# For LiteLLM
cp litellm_config.example.yaml litellm_config.yaml
cp providers.litellm.example.yaml providers.yaml
litellm --config litellm_config.yaml

# For Portkey
cp providers.portkey.example.yaml providers.yaml
# Edit providers.yaml with your Portkey keys
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

- [Portkey Proxy Guide](PORTKEY_PROXY.md) - Complete Portkey setup
- [LiteLLM Proxy Guide](LITELLM_PROXY.md) - Complete LiteLLM setup
- [Generic Provider Quick Start](GENERIC_PROVIDER_QUICKSTART.md) - Quick generic provider setup
- [Generic Provider Guide](GENERIC_PROVIDER.md) - Complete generic provider documentation
- [Proxy Quick Start](PROXY_QUICKSTART.md) - Quick proxy setup guide