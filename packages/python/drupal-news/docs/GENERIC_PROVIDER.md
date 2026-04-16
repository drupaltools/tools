# Generic Provider Guide

## Overview

The **generic provider** is a universal client that works with **any OpenAI-compatible API endpoint**. Use it when you want to:

- Try new AI services without writing code
- Use multiple models from the same service
- Connect to custom or self-hosted endpoints
- Avoid creating dedicated provider clients

## When to Use

✅ **Use generic provider when:**
- Service has OpenAI-compatible API format
- You want to test a new service quickly
- You need multiple models from one service
- You have a custom/self-hosted endpoint
- Service isn't in the built-in providers list

⚠️ **Use dedicated provider when:**
- Service has a specialized SDK (better error handling)
- You need service-specific features
- Service is widely used (better support)

## Quick Start

For basic setup and quick configuration, see:

**[Generic Provider Quick Start](GENERIC_PROVIDER_QUICKSTART.md)** - Complete quick start guide with basic configurations for popular services.

## Service Configurations

For detailed service-specific configurations and examples:

**[Generic Provider Services](GENERIC_PROVIDER_SERVICES.md)** - Complete guide for configuring:
- OpenRouter (100+ models)
- Groq (fast inference)
- Perplexity (online models)
- Together AI
- Fireworks AI
- Azure OpenAI
- LiteLLM Proxy
- Custom self-hosted endpoints

## Advanced Configurations

For advanced usage patterns and complex setups:

**[Generic Provider Advanced](GENERIC_PROVIDER_ADVANCED.md)** - Advanced configurations including:
- Multiple models from same service
- Custom headers and metadata
- Environment variable usage
- Provider naming strategies
- Configuration templates

## Testing and Troubleshooting

For testing methods and troubleshooting common issues:

**[Generic Provider Testing](GENERIC_PROVIDER_TESTING.md)** - Complete testing and troubleshooting guide:
- Testing with cached sources
- Comparing model outputs
- Common error solutions
- Performance optimization
- Debugging techniques

## Best Practices

For security, performance, and maintenance best practices:

**[Generic Provider Best Practices](GENERIC_PROVIDER_BEST_PRACTICES.md)** - Best practices for:
- Security and API key management
- Configuration organization
- Performance optimization
- Testing and validation
- Maintenance and monitoring

## Examples

See `providers.generic.example.yaml` for complete working examples of:
- OpenRouter (multiple models)
- Together AI
- Groq
- Perplexity
- Fireworks AI
- Azure OpenAI
- LiteLLM
- Custom endpoints

## See Also

- [Custom API URLs Guide](CUSTOM_API_URLS.md) - Proxy configuration
- [Proxy Quick Start](PROXY_QUICKSTART.md) - LiteLLM and Portkey setup
- [Usage Guide](../USAGE.md) - Basic usage patterns
- `providers.generic.example.yaml` - Ready-to-use configurations