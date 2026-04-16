# Generic Provider - Advanced Configurations

This document covers advanced configurations for the generic provider, including multiple models, custom headers, and environment variable usage.

## Multiple Models from Same Service

You can configure multiple providers using the same service but different models.

### Example: Multiple OpenRouter Models

```yaml
providers:
  # Llama 3.1 70B
  llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer ${OPENROUTER_API_KEY}

  # Claude 3.5 Sonnet
  claude-sonnet:
    client: generic_client
    model: anthropic/claude-3.5-sonnet
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer ${OPENROUTER_API_KEY}

  # Gemini Pro 1.5
  gemini-pro:
    client: generic_client
    model: google/gemini-pro-1.5
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer ${OPENROUTER_API_KEY}

  # GPT-4
  gpt-4:
    client: generic_client
    model: openai/gpt-4
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer ${OPENROUTER_API_KEY}
```

### Usage

```bash
# Use different models for different runs
./index.py --provider llama-70b --days 7
./index.py --provider claude-sonnet --days 7
./index.py --provider gemini-pro --days 7
```

## Custom Headers

Custom headers allow you to pass additional metadata and configuration to the API.

### Basic Custom Headers

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

### Service-Specific Headers

#### OpenRouter Headers

```yaml
generic:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.2
  api_url: https://openrouter.ai/api/v1
  headers:
    Authorization: Bearer ${OPENROUTER_API_KEY}
    HTTP-Referer: https://your-domain.com
    X-Title: Your Application Name
    X-Version: 1.0.0
```

#### Portkey Headers

```yaml
generic:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.2
  api_url: https://api.portkey.ai/v1
  headers:
    x-portkey-api-key: ${PORTKEY_API_KEY}
    x-portkey-virtual-key: ${PORTKEY_MODEL_KEY}
    x-portkey-trace-id: drupal-news-{date}
    x-portkey-metadata: '{"source":"drupal-aggregator","environment":"production"}'
```

#### Custom Service Headers

```yaml
custom:
  client: generic_client
  model: your-model
  temperature: 0.2
  api_url: https://your-service.com/v1
  headers:
    Authorization: Bearer ${CUSTOM_API_KEY}
    X-Client-ID: drupal-aggregator
    X-Client-Version: 1.0.0
    X-Request-ID: $(date +%s)
    X-Environment: production
```

## Environment Variables

Use environment variables for better security and configuration management.

### Basic Environment Variables

```bash
# .env
GENERIC_API_KEY=sk-or-v1-xxx
GENERIC_API_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=sk-or-v1-xxx
TOGETHER_API_KEY=xxx
GROQ_API_KEY=gsk_xxx
PERPLEXITY_API_KEY=pplx-xxx
FIREWORKS_API_KEY=fw-xxx
AZURE_OPENAI_API_KEY=xxx
```

### Configuration with Environment Variables

```yaml
# providers.yaml - uses environment variables
providers:
  # Generic provider using environment variables
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    # api_url from GENERIC_API_URL
    # Authorization from GENERIC_API_KEY

  # OpenRouter with environment variable
  openrouter:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer ${OPENROUTER_API_KEY}

  # Together AI with environment variable
  together:
    client: generic_client
    model: mistralai/Mixtral-8x7B-Instruct-v0.1
    temperature: 0.2
    api_url: https://api.together.xyz/v1
    headers:
      Authorization: Bearer ${TOGETHER_API_KEY}

  # Groq with environment variable
  groq:
    client: generic_client
    model: llama-3.1-70b-versatile
    temperature: 0.2
    api_url: https://api.groq.com/openai/v1
    headers:
      Authorization: Bearer ${GROQ_API_KEY}
```

### Advanced Environment Variable Usage

#### Conditional Configuration

```yaml
providers:
  production:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    api_url: ${PRODUCTION_API_URL}
    headers:
      Authorization: Bearer ${PRODUCTION_API_KEY}

  development:
    client: generic_client
    model: meta-llama/llama-3.1-8b-instruct
    temperature: 0.2
    api_url: ${DEVELOPMENT_API_URL}
    headers:
      Authorization: Bearer ${DEVELOPMENT_API_KEY}
```

#### Dynamic Headers

```yaml
providers:
  generic:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    temperature: 0.2
    api_url: https://openrouter.ai/api/v1
    headers:
      Authorization: Bearer ${OPENROUTER_API_KEY}
      X-Request-ID: $(date +%s-%N)
      X-Environment: ${NODE_ENV:-development}
```

## Provider Naming Strategies

### Descriptive Names

Use descriptive names for better organization:

```yaml
providers:
  # Service-Model naming
  openrouter-llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct

  openrouter-claude-sonnet:
    client: generic_client
    model: anthropic/claude-3.5-sonnet

  groq-llama-70b:
    client: generic_client
    model: llama-3.1-70b-versatile

  # Purpose-based naming
  production-ai:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct

  development-ai:
    client: generic_client
    model: meta-llama/llama-3.1-8b-instruct

  testing-ai:
    client: generic_client
    model: meta-llama/llama-3.1-8b-instruct
```

### Environment-Specific Names

```yaml
providers:
  # Production environment
  prod-llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    api_url: https://production-api.example.com/v1

  # Staging environment
  staging-llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct
    api_url: https://staging-api.example.com/v1

  # Development environment
  dev-llama-8b:
    client: generic_client
    model: meta-llama/llama-3.1-8b-instruct
    api_url: https://dev-api.example.com/v1
```

## Configuration Templates

### Template for New Services

```yaml
# Template for new AI service
service-name:
  client: generic_client
  model: model-name-from-service
  temperature: 0.2
  api_url: https://api.service.com/v1
  headers:
    Authorization: Bearer ${SERVICE_API_KEY}
    # Optional headers
    X-Client-ID: drupal-aggregator
    X-Client-Version: 1.0.0
```

### Template for Local Development

```yaml
# Template for local development
local-dev:
  client: generic_client
  model: local-model-name
  temperature: 0.2
  api_url: http://localhost:8080/v1
  headers:
    Authorization: Bearer ${LOCAL_API_KEY}
    # Development headers
    X-Environment: development
    X-Debug: true
```

## Best Practices for Advanced Configurations

### 1. Use Environment Variables for Secrets

```yaml
# Good
headers:
  Authorization: Bearer ${API_KEY}

# Bad
headers:
  Authorization: Bearer sk-hardcoded-key
```

### 2. Document Custom Configurations

```yaml
# Custom endpoint with documentation
corporate-ai:
  client: generic_client
  model: corporate-model-v2
  temperature: 0.2
  api_url: https://internal.company.com/ai/v1
  # Note: Internal AI gateway, uses corporate authentication
  # Requires COMPANY_AI_TOKEN environment variable
  headers:
    Authorization: Bearer ${COMPANY_AI_TOKEN}
    X-Client-ID: drupal-aggregator
```

### 3. Use Descriptive Provider Names

```yaml
# Good - clear what service and model
openrouter-llama-70b:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct

# Less clear
generic:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
```

### 4. Test Configurations

```bash
# Test new configurations with cached sources
./index.py --provider new-config --use-sources latest --email no
```

## See Also

- [Generic Provider Quick Start](GENERIC_PROVIDER_QUICKSTART.md) - Basic setup
- [Generic Provider Services](GENERIC_PROVIDER_SERVICES.md) - Service-specific configurations
- [Generic Provider Testing](GENERIC_PROVIDER_TESTING.md) - Testing and troubleshooting
- [Generic Provider Best Practices](GENERIC_PROVIDER_BEST_PRACTICES.md) - Best practices