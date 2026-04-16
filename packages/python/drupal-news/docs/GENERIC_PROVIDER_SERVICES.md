# Generic Provider - Service Configurations

This document provides detailed configuration examples for various AI services using the generic provider.

## Supported Services

The generic provider works with any service implementing the OpenAI chat completions format.

## OpenRouter (100+ Models)

OpenRouter provides access to 100+ models from various providers through a unified API.

### Basic Configuration

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

### Popular OpenRouter Models

- `meta-llama/llama-3.1-70b-instruct` - Meta's Llama 3.1 70B
- `anthropic/claude-3.5-sonnet` - Anthropic Claude 3.5 Sonnet
- `google/gemini-pro-1.5` - Google Gemini Pro 1.5
- `openai/gpt-4` - OpenAI GPT-4
- `mistralai/mixtral-8x7b-instruct` - Mistral Mixtral 8x7B
- `nousresearch/hermes-3-llama-3.1-405b` - Hermes 3 405B
- `qwen/qwen2.5-72b-instruct` - Alibaba Qwen 2.5 72B

### Advanced OpenRouter Headers

```yaml
generic:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.2
  api_url: https://openrouter.ai/api/v1
  headers:
    Authorization: Bearer ${OPENROUTER_API_KEY}
    HTTP-Referer: https://drupal-news.example.com
    X-Title: Drupal News Aggregator
    X-Custom-Header: custom-value
```

## Groq (Fast Inference)

Groq provides extremely fast inference with optimized models.

### Basic Configuration

```yaml
groq:
  client: generic_client
  model: llama-3.1-70b-versatile
  temperature: 0.2
  api_url: https://api.groq.com/openai/v1
  headers:
    Authorization: Bearer ${GROQ_API_KEY}
```

### Available Groq Models

- `llama-3.1-70b-versatile` - Llama 3.1 70B (recommended)
- `llama-3.1-8b-instant` - Llama 3.1 8B (fastest)
- `mixtral-8x7b-32768` - Mixtral 8x7B (32K context)
- `gemma2-9b-it` - Google Gemma 2 9B

### Performance Notes

Groq is optimized for speed:
- Responses typically under 2 seconds
- High throughput
- Best for real-time applications

## Perplexity (Online Models)

Perplexity provides models with internet access for up-to-date information.

### Basic Configuration

```yaml
perplexity:
  client: generic_client
  model: llama-3.1-sonar-large-128k-online
  temperature: 0.2
  api_url: https://api.perplexity.ai
  headers:
    Authorization: Bearer ${PERPLEXITY_API_KEY}
```

### Available Perplexity Models

- `llama-3.1-sonar-large-128k-online` - Online model with 128K context
- `llama-3.1-sonar-small-128k-online` - Smaller online model
- `llama-3.1-sonar-huge-128k-online` - Largest online model

### Online Model Features

- Real-time web search capabilities
- Up-to-date information
- Large context windows
- Best for current events and news

## Together AI

Together AI provides access to various open-source models.

### Basic Configuration

```yaml
together:
  client: generic_client
  model: mistralai/Mixtral-8x7B-Instruct-v0.1
  temperature: 0.2
  api_url: https://api.together.xyz/v1
  headers:
    Authorization: Bearer ${TOGETHER_API_KEY}
```

### Popular Together AI Models

- `mistralai/Mixtral-8x7B-Instruct-v0.1` - Mixtral 8x7B
- `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` - Llama 3.1 70B
- `Qwen/Qwen2.5-72B-Instruct` - Qwen 2.5 72B
- `codellama/CodeLlama-70b-Instruct-hf` - CodeLlama 70B

## Fireworks AI

Fireworks AI provides optimized inference for various models.

### Basic Configuration

```yaml
fireworks:
  client: generic_client
  model: accounts/fireworks/models/llama-v3p1-70b-instruct
  temperature: 0.2
  api_url: https://api.fireworks.ai/inference/v1
  headers:
    Authorization: Bearer ${FIREWORKS_API_KEY}
```

### Available Fireworks AI Models

- `accounts/fireworks/models/llama-v3p1-70b-instruct` - Llama 3.1 70B
- `accounts/fireworks/models/llama-v3p1-8b-instruct` - Llama 3.1 8B
- `accounts/fireworks/models/mixtral-8x22b-instruct` - Mixtral 8x22B

## Azure OpenAI

Azure OpenAI provides managed OpenAI models with enterprise features.

### Basic Configuration

```yaml
azure:
  client: generic_client
  model: gpt-4  # Your deployment name
  temperature: 0.2
  api_url: https://YOUR-RESOURCE.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT
  headers:
    api-key: ${AZURE_OPENAI_API_KEY}
```

### Azure Configuration Notes

- **Resource Name**: Replace `YOUR-RESOURCE` with your Azure resource name
- **Deployment Name**: Replace `YOUR-DEPLOYMENT` with your model deployment name
- **API Key**: Use the Azure OpenAI API key, not OpenAI API key

### Example with Real Values

```yaml
azure:
  client: generic_client
  model: gpt-4
  temperature: 0.2
  api_url: https://mycompany.openai.azure.com/openai/deployments/gpt-4-deployment
  headers:
    api-key: ${AZURE_OPENAI_API_KEY}
```

## LiteLLM Proxy

Use LiteLLM as a proxy for unified access to multiple providers.

### Basic Configuration

```yaml
litellm:
  client: generic_client
  model: gpt-4  # Model from litellm_config.yaml
  temperature: 0.2
  api_url: http://localhost:4000
```

### With Authentication

If LiteLLM proxy has authentication enabled:

```yaml
litellm:
  client: generic_client
  model: gpt-4
  temperature: 0.2
  api_url: http://localhost:4000
  headers:
    Authorization: Bearer your-litellm-master-key
```

## Custom Self-Hosted Endpoints

Connect to any custom OpenAI-compatible API.

### Basic Configuration

```yaml
custom:
  client: generic_client
  model: your-model-name
  temperature: 0.2
  api_url: https://your-endpoint.com/v1
  headers:
    Authorization: Bearer your-token
```

### Example: Local Development

```yaml
local:
  client: generic_client
  model: local-model
  temperature: 0.2
  api_url: http://localhost:8080/v1
  headers:
    Authorization: Bearer local-token
```

### Example: Corporate Gateway

```yaml
corporate:
  client: generic_client
  model: corporate-ai-model
  temperature: 0.2
  api_url: https://internal.company.com/ai/v1
  headers:
    Authorization: Bearer ${COMPANY_AI_TOKEN}
    X-Client-ID: drupal-aggregator
```

## Service Comparison

| Service | Speed | Cost | Best For |
|---------|-------|------|----------|
| **Groq** | ⭐⭐⭐⭐⭐ | Medium | Real-time, high throughput |
| **OpenRouter** | ⭐⭐⭐⭐ | Low | Model variety, cost-effective |
| **Perplexity** | ⭐⭐⭐ | High | Current events, web search |
| **Together AI** | ⭐⭐⭐ | Low | Open-source models |
| **Fireworks AI** | ⭐⭐⭐⭐ | Medium | Optimized inference |
| **Azure OpenAI** | ⭐⭐⭐⭐ | High | Enterprise, compliance |

## See Also

- [Generic Provider Quick Start](GENERIC_PROVIDER_QUICKSTART.md) - Quick setup guide
- [Generic Provider Advanced](GENERIC_PROVIDER_ADVANCED.md) - Advanced configurations
- [Generic Provider Testing](GENERIC_PROVIDER_TESTING.md) - Testing and troubleshooting
- [Generic Provider Best Practices](GENERIC_PROVIDER_BEST_PRACTICES.md) - Best practices