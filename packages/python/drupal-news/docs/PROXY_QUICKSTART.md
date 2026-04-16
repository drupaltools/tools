# Proxy Quick Start Guide

## LiteLLM (Self-Hosted)

### Setup in 5 minutes

```bash
# 1. Install LiteLLM
pip install litellm[proxy]

# 2. Copy and edit configuration
cp litellm_config.example.yaml litellm_config.yaml
# Edit: Add your API keys from .env

# 3. Start proxy server
litellm --config litellm_config.yaml
# Runs on http://localhost:4000

# 4. Configure aggregator
cp providers.litellm.example.yaml providers.yaml

# 5. Run
./index.py --provider openai --days 7
```

### Advantages
- ✅ Free and open source
- ✅ Full data privacy
- ✅ Load balancing across API keys
- ✅ Redis caching
- ✅ Fallback chains
- ✅ 100+ LLM support

### When to use
- You want full control
- Privacy is important
- You need load balancing
- You have multiple API keys
- You want to minimize costs with caching

---

## Portkey (Cloud)

### Setup in 2 minutes

```bash
# 1. Sign up at https://portkey.ai
# Get: API key + virtual keys

# 2. Configure aggregator
cp providers.portkey.example.yaml providers.yaml
# Edit: Add your Portkey keys

# 3. Run
./index.py --provider grok --days 7
```

### Advantages
- ✅ Zero infrastructure
- ✅ Beautiful dashboard
- ✅ Request tracing
- ✅ Advanced analytics
- ✅ Instant setup

### When to use
- You want quick setup
- You need monitoring dashboard
- You want detailed analytics
- Infrastructure management not needed

---

## Comparison Table

| Feature | LiteLLM | Portkey | Direct API |
|---------|---------|---------|------------|
| **Setup Time** | 5 min | 2 min | 0 min |
| **Cost** | Free | Paid tier | API costs only |
| **Privacy** | ✅ Local | ⚠️ Cloud | ✅ Direct |
| **Dashboard** | Basic | ✅ Full | None |
| **Load Balancing** | ✅ Yes | ✅ Yes | Manual |
| **Caching** | ✅ Redis | ✅ Built-in | None |
| **Fallbacks** | ✅ Yes | ✅ Yes | Manual |
| **Maintenance** | You manage | They manage | None needed |

---

## Example Configurations

### LiteLLM: All providers through one proxy

```yaml
# providers.yaml
default_provider: openai

providers:
  openai:
    client: openai_client
    model: gpt-4.1-mini
    temperature: 0.2
    api_url: http://localhost:4000

  anthropic:
    client: openai_client
    model: claude-3-5-sonnet
    temperature: 0.2
    api_url: http://localhost:4000

  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2
    api_url: http://localhost:4000
```

### Portkey: Specific providers

```yaml
# providers.yaml
providers:
  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2
    api_url: https://api.portkey.ai/v1
    headers:
      x-portkey-api-key: pk-YOUR-KEY
      x-portkey-virtual-key: vk-GROK-KEY

  openai:
    client: openai_client
    model: gpt-4.1-mini
    temperature: 0.2
    api_url: https://api.portkey.ai/v1
    headers:
      x-portkey-api-key: pk-YOUR-KEY
      x-portkey-virtual-key: vk-OPENAI-KEY
```

### Mixed: Some through proxy, some direct

```yaml
# providers.yaml
providers:
  openai:
    client: openai_client
    model: gpt-4.1-mini
    temperature: 0.2
    api_url: http://localhost:4000  # Via LiteLLM

  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2
    api_url: https://api.portkey.ai/v1  # Via Portkey
    headers:
      x-portkey-api-key: pk-YOUR-KEY
      x-portkey-virtual-key: vk-GROK-KEY

  ollama:
    client: ollama_client
    model: qwen2.5:7b-instruct
    temperature: 0.2
    # No api_url = direct connection to local Ollama
```

---

## Testing Your Setup

### 1. Test without AI (fetch only)
```bash
./index.py --fetch-only
```

### 2. Test with cached sources (no re-fetch)
```bash
./index.py --provider openai --use-sources 2025-10-25 --email no
```

### 3. Test different providers
```bash
# Test each provider through your proxy
./index.py --provider openai --use-sources 2025-10-25 --email no
./index.py --provider anthropic --use-sources 2025-10-25 --email no
./index.py --provider grok --use-sources 2025-10-25 --email no
```

### 4. Check logs
```bash
# LiteLLM logs (in terminal where server runs)
# Aggregator logs
tail -f runs/YYYY-MM-DD/run.log
```

---

## Troubleshooting

### LiteLLM proxy not starting
```bash
# Check if port 4000 is in use
lsof -i :4000

# Use different port
litellm --config litellm_config.yaml --port 8000

# Update providers.yaml with new port
api_url: http://localhost:8000
```

### Portkey authentication errors
```bash
# Verify keys in providers.yaml
# Check: x-portkey-api-key (starts with pk-)
# Check: x-portkey-virtual-key (starts with vk-)
```

### Connection refused
```bash
# LiteLLM: Ensure server is running
ps aux | grep litellm

# Check URL in providers.yaml matches server
```

### Wrong API called
```bash
# Check model names match litellm_config.yaml
# LiteLLM uses model_name to route requests
```

---

## Advanced Features

### LiteLLM: Load balancing
```yaml
# litellm_config.yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY_1

  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY_2
```

### LiteLLM: Fallback chains
```yaml
# litellm_config.yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY
      fallbacks:
        - model: anthropic/claude-3-5-sonnet
```

### Portkey: Request tracing
```yaml
# providers.yaml
grok:
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: pk-YOUR-KEY
    x-portkey-virtual-key: vk-GROK-KEY
    x-portkey-trace-id: drupal-news-{date}
```

---

## See Also

- [Full Documentation](CUSTOM_API_URLS.md) - Comprehensive guide
- [LiteLLM Docs](https://docs.litellm.ai) - Official documentation
- [Portkey Docs](https://docs.portkey.ai) - Official documentation
