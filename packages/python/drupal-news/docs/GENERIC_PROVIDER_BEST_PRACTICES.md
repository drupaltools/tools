# Generic Provider - Best Practices

This document covers best practices for using the generic provider effectively and securely.

## Security Best Practices

### Use Environment Variables for API Keys

Never hardcode API keys in configuration files:

```yaml
# Good - uses environment variable
headers:
  Authorization: Bearer ${OPENROUTER_API_KEY}

# Bad - hardcoded key (security risk)
headers:
  Authorization: Bearer sk-or-hardcoded-key-here
```

### Environment Variable Setup

```bash
# .env - Store all API keys securely
OPENROUTER_API_KEY=sk-or-v1-xxx
GROQ_API_KEY=gsk_xxx
TOGETHER_API_KEY=xxx
PERPLEXITY_API_KEY=pplx-xxx
FIREWORKS_API_KEY=fw-xxx
AZURE_OPENAI_API_KEY=xxx
```

### Rotate API Keys Regularly

- Set reminders to rotate API keys every 90 days
- Monitor usage for suspicious activity
- Revoke unused keys immediately

### Use Service-Specific Keys

Use different API keys for different services:

```bash
# .env
OPENROUTER_API_KEY=sk-or-v1-openrouter-key
GROQ_API_KEY=gsk-groq-key
TOGETHER_API_KEY=together-key
```

## Configuration Best Practices

### Use Descriptive Provider Names

Choose clear, descriptive names for your providers:

```yaml
# Good - clear what service and model
providers:
  openrouter-llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct

  groq-llama-70b:
    client: generic_client
    model: llama-3.1-70b-versatile

  openrouter-claude-sonnet:
    client: generic_client
    model: anthropic/claude-3.5-sonnet

# Less clear - generic names
providers:
  generic1:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct

  generic2:
    client: generic_client
    model: llama-3.1-70b-versatile
```

### Document Custom Configurations

Add comments to document complex configurations:

```yaml
# Custom endpoint with documentation
corporate-ai:
  client: generic_client
  model: corporate-model-v2
  temperature: 0.2
  api_url: https://internal.company.com/ai/v1
  # Note: Internal AI gateway, uses corporate authentication
  # Requires COMPANY_AI_TOKEN environment variable
  # Model: Custom fine-tuned model for news summarization
  headers:
    Authorization: Bearer ${COMPANY_AI_TOKEN}
    X-Client-ID: drupal-aggregator
    X-Environment: production
```

### Use Consistent Naming Conventions

Follow consistent naming patterns:

```yaml
# Service-Model naming convention
providers:
  openrouter-llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct

  openrouter-claude-35-sonnet:
    client: generic_client
    model: anthropic/claude-3.5-sonnet

  groq-llama-70b:
    client: generic_client
    model: llama-3.1-70b-versatile

# Environment-Service-Model naming
providers:
  prod-openrouter-llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct

  staging-openrouter-llama-70b:
    client: generic_client
    model: meta-llama/llama-3.1-70b-instruct

  dev-openrouter-llama-8b:
    client: generic_client
    model: meta-llama/llama-3.1-8b-instruct
```

## Performance Best Practices

### Choose Appropriate Models

Select models based on your performance requirements:

```yaml
# High performance (fast response)
groq-llama-70b:
  client: generic_client
  model: llama-3.1-70b-versatile
  # Groq provides very fast inference

# Cost-effective (good balance)
openrouter-llama-70b:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  # OpenRouter offers good performance at lower cost

# Best quality (slower)
openrouter-claude-35-sonnet:
  client: generic_client
  model: anthropic/claude-3.5-sonnet
  # Claude provides excellent quality but slower
```

### Optimize Temperature Settings

Use appropriate temperature for your use case:

```yaml
# Factual reporting (low temperature)
news-summary:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.1  # More deterministic, factual

# Creative content (higher temperature)
creative-writing:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.7  # More creative, varied

# Balanced (default)
balanced:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.2  # Good balance for most use cases
```

### Use Caching Effectively

Leverage caching to reduce API calls:

```bash
# Fetch data once, test multiple models
./index.py --fetch-only
./index.py --provider model1 --use-sources latest --email no
./index.py --provider model2 --use-sources latest --email no
./index.py --provider model3 --use-sources latest --email no
```

## Testing Best Practices

### Test Before Production

Always test new configurations with cached sources:

```bash
# Test with cached data first
./index.py --provider new-config --use-sources latest --email no

# Compare with existing configuration
./index.py --provider existing-config --use-sources latest --email no
```

### Validate Configuration

Use dry-run to validate configuration:

```bash
# Validate configuration without API calls
./index.py --provider new-config --dry-run

# Check for configuration errors
./index.py --provider new-config --dry-run --verbose
```

### Monitor Performance

Track performance metrics:

```bash
# Check run metrics
cat runs/$(date +%Y-%m-%d)/metrics.json

# Monitor response times
grep "duration" runs/$(date +%Y-%m-%d)/metrics.json
```

## Maintenance Best Practices

### Regular Configuration Review

Review and update configurations regularly:

- Check for deprecated models
- Update to newer model versions
- Verify API endpoints are still active
- Remove unused provider configurations

### Monitor API Usage

Keep track of API usage and costs:

- Set up usage alerts with your AI service
- Monitor cost dashboards regularly
- Implement usage limits if needed
- Track performance metrics over time

### Backup Configurations

Keep backups of working configurations:

```bash
# Backup providers.yaml
cp providers.yaml providers.yaml.backup

# Version control configurations
git add providers.yaml
git commit -m "Update provider configurations"
```

## Error Handling Best Practices

### Implement Graceful Degradation

Plan for service outages:

```yaml
# Primary provider
primary-ai:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  api_url: https://primary-service.com/v1

# Fallback provider
fallback-ai:
  client: generic_client
  model: meta-llama/llama-3.1-8b-instruct
  api_url: https://fallback-service.com/v1
```

### Monitor Error Rates

Track and analyze errors:

```bash
# Check for errors in logs
grep -i "error" runs/$(date +%Y-%m-%d)/run.log

# Monitor success rates
cat runs/$(date +%Y-%m-%d)/metrics.json | jq '.success_rate'
```

## Examples and Templates

### Production Configuration Template

```yaml
# Production configuration template
prod-openrouter-llama-70b:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.2
  api_url: https://openrouter.ai/api/v1
  # Production settings
  headers:
    Authorization: Bearer ${OPENROUTER_API_KEY}
    HTTP-Referer: https://drupal-news.example.com
    X-Title: Drupal News Aggregator
    X-Environment: production
```

### Development Configuration Template

```yaml
# Development configuration template
dev-openrouter-llama-8b:
  client: generic_client
  model: meta-llama/llama-3.1-8b-instruct
  temperature: 0.2
  api_url: https://openrouter.ai/api/v1
  # Development settings
  headers:
    Authorization: Bearer ${OPENROUTER_API_KEY}
    HTTP-Referer: https://dev.drupal-news.example.com
    X-Title: Drupal News Aggregator (Dev)
    X-Environment: development
```

### Testing Configuration Template

```yaml
# Testing configuration template
test-groq-llama-8b:
  client: generic_client
  model: llama-3.1-8b-instant
  temperature: 0.2
  api_url: https://api.groq.com/openai/v1
  # Testing settings - fast and cost-effective
  headers:
    Authorization: Bearer ${GROQ_API_KEY}
    X-Environment: testing
```

## See Also

- [Generic Provider Quick Start](GENERIC_PROVIDER_QUICKSTART.md) - Basic setup
- [Generic Provider Services](GENERIC_PROVIDER_SERVICES.md) - Service-specific configurations
- [Generic Provider Advanced](GENERIC_PROVIDER_ADVANCED.md) - Advanced configurations
- [Generic Provider Testing](GENERIC_PROVIDER_TESTING.md) - Testing and troubleshooting