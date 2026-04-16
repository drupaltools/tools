# Generic Provider Quick Start

The **generic provider** is a universal client that works with **any OpenAI-compatible API endpoint**.

## Overview

Use the generic provider when you want to:
- Try new AI services without writing code
- Use multiple models from the same service
- Connect to custom or self-hosted endpoints
- Avoid creating dedicated provider clients

## Quick Setup

### Basic Configuration

```yaml
# providers.yaml
providers:
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer your-api-key-here
```

### Environment Variables (Alternative)

Instead of hardcoding in YAML:

```bash
# .env
GENERIC_API_KEY=your-api-key
GENERIC_API_URL=https://openrouter.ai/api/v1
```

```yaml
# providers.yaml - uses environment variables
providers:
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    # Automatically uses GENERIC_API_KEY and GENERIC_API_URL
```

### Run

```bash
./index.py --provider generic --days 7
```

## Supported Services

The generic provider works with any service implementing the OpenAI chat completions format.

### OpenRouter (100+ Models)

```yaml
generic:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.2
  api_url: https://openrouter.ai/api/v1
  headers:
    Authorization: Bearer ${OPENROUTER_API_KEY}
    HTTP-Referer: https://your-site.com  # Optional
    X-Title: Drupal News  # Optional
```

**Popular OpenRouter models:**
- `meta-llama/llama-3.1-70b-instruct`
- `anthropic/claude-3.5-sonnet`
- `google/gemini-pro-1.5`
- `openai/gpt-4`
- `mistralai/mixtral-8x7b-instruct`

### Groq (Fast Inference)

```yaml
groq:
  client: generic_client
  model: llama-3.1-70b-versatile
  temperature: 0.2
  api_url: https://api.groq.com/openai/v1
  headers:
    Authorization: Bearer ${GROQ_API_KEY}
```

**Available Groq models:**
- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

### Perplexity (Online Models)

```yaml
perplexity:
  client: generic_client
  model: llama-3.1-sonar-large-128k-online
  temperature: 0.2
  api_url: https://api.perplexity.ai
  headers:
    Authorization: Bearer ${PERPLEXITY_API_KEY}
```

### Together AI

```yaml
together:
  client: generic_client
  model: mistralai/Mixtral-8x7B-Instruct-v0.1
  temperature: 0.2
  api_url: https://api.together.xyz/v1
  headers:
    Authorization: Bearer ${TOGETHER_API_KEY}
```

### Fireworks AI

```yaml
fireworks:
  client: generic_client
  model: accounts/fireworks/models/llama-v3p1-70b-instruct
  temperature: 0.2
  api_url: https://api.fireworks.ai/inference/v1
  headers:
    Authorization: Bearer ${FIREWORKS_API_KEY}
```

### Azure OpenAI

```yaml
azure:
  client: generic_client
  model: gpt-4  # Your deployment name
  temperature: 0.2
  api_url: https://YOUR-RESOURCE.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT
  headers:
    api-key: ${AZURE_OPENAI_API_KEY}
```

### LiteLLM Proxy

```yaml
litellm:
  client: generic_client
  model: gpt-4  # Model from litellm_config.yaml
  temperature: 0.2
  api_url: http://localhost:4000
```

### Custom Self-Hosted

```yaml
custom:
  client: generic_client
  model: your-model-name
  temperature: 0.2
  api_url: https://your-endpoint.com/v1
  headers:
    Authorization: Bearer your-token
```

## Testing

### Test with Cached Sources

```bash
# Fetch data once
./index.py --fetch-only

# Test different models without re-fetching
./index.py --provider generic --use-sources 2025-10-25 --email no
```

### Compare Model Outputs

```bash
# Generate summaries with different models
DATE=$(date +%Y-%m-%d)

./index.py --provider generic --use-sources $DATE --email no
mv runs/$DATE/summary.md runs/$DATE/summary_generic.md

# Compare outputs
diff runs/$DATE/summary_generic.md runs/$DATE/summary_other.md
```

## Quick Start Examples

The repository includes ready-to-use configuration examples:

```bash
# For generic provider
cp providers.generic.example.yaml providers.yaml
# Edit providers.yaml with your API keys
```

## Troubleshooting

### Error: "API URL required"

```
ValueError: API URL required. Provide via api_url parameter or GENERIC_API_URL environment variable.
```

**Solution:** Set `api_url` in providers.yaml or `GENERIC_API_URL` in .env:

```yaml
generic:
  api_url: https://openrouter.ai/api/v1  # Add this
```

### Error: HTTP 401 Unauthorized

```
RuntimeError: Generic API HTTP error: 401
```

**Solution:** Check your API key:
1. Verify key is correct in .env or providers.yaml
2. Check Authorization header format
3. Ensure key has proper permissions

### Error: HTTP 404 Not Found

```
RuntimeError: Generic API HTTP error: 404
```

**Solution:** Check API URL and model name:
1. Verify URL ends with `/v1` or correct version
2. Check model name is valid for that service
3. Some services require full paths (e.g., Azure)

## Best Practices

### Use Environment Variables for Keys

```yaml
# Good
headers:
  Authorization: Bearer ${OPENROUTER_API_KEY}

# Bad (security risk)
headers:
  Authorization: Bearer sk-or-hardcoded-key
```

### Name Providers Descriptively

```yaml
# Good
providers:
  openrouter-llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct

# Less clear
providers:
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
```

### Test Before Production

```bash
# Always test new configurations with cached sources
./index.py --provider new-provider --use-sources latest --email no
```

## See Also

- [Generic Provider Guide](GENERIC_PROVIDER.md) - Complete documentation
- [Portkey Proxy Guide](PORTKEY_PROXY.md)
- [LiteLLM Proxy Guide](LITELLM_PROXY.md)
- [Proxy Quick Start](PROXY_QUICKSTART.md)