# Generic Provider - Testing and Troubleshooting

This document covers testing methods and troubleshooting for the generic provider.

## Testing Methods

### Test with Cached Sources

Test different models without re-fetching data:

```bash
# Fetch data once
./index.py --fetch-only

# Test different models without re-fetching
./index.py --provider generic --use-sources 2025-10-25 --email no
./index.py --provider llama-70b --use-sources 2025-10-25 --email no
./index.py --provider claude-sonnet --use-sources 2025-10-25 --email no
```

### Compare Model Outputs

Generate summaries with different models and compare results:

```bash
# Generate summaries with different models
DATE=$(date +%Y-%m-%d)

./index.py --provider llama-70b --use-sources $DATE --email no
mv runs/$DATE/summary.md runs/$DATE/summary_llama70b.md

./index.py --provider claude-sonnet --use-sources $DATE --email no
mv runs/$DATE/summary.md runs/$DATE/summary_claude.md

./index.py --provider gemini-pro --use-sources $DATE --email no
mv runs/$DATE/summary.md runs/$DATE/summary_gemini.md

# Compare outputs
diff runs/$DATE/summary_llama70b.md runs/$DATE/summary_claude.md
diff runs/$DATE/summary_llama70b.md runs/$DATE/summary_gemini.md
```

### Dry Run Testing

Test configuration without making API calls:

```bash
# Dry run to verify config loads
./index.py --provider generic --dry-run

# Dry run with specific date
./index.py --provider generic --use-sources 2025-10-25 --dry-run
```

### Fetch-Only Testing

Test data collection without AI processing:

```bash
# Fetch-only (no API calls)
./index.py --fetch-only

# Fetch with specific timeframe
./index.py --fetch-only --days 3
```

## Troubleshooting

### Error: "API URL required"

```
ValueError: API URL required. Provide via api_url parameter or GENERIC_API_URL environment variable.
```

**Solution:** Set `api_url` in providers.yaml or `GENERIC_API_URL` in .env:

```yaml
generic:
  client: generic_client
  model: meta-llama/llama-3.1-70b-instruct
  temperature: 0.2
  api_url: https://openrouter.ai/api/v1  # Add this
  headers:
    Authorization: Bearer ${OPENROUTER_API_KEY}
```

### Error: HTTP 401 Unauthorized

```
RuntimeError: Generic API HTTP error: 401
```

**Solution:** Check your API key:

1. **Verify key is correct** in .env or providers.yaml
2. **Check Authorization header format**:
   ```yaml
   headers:
     Authorization: Bearer your-api-key  # Check format
   ```
3. **Ensure key has proper permissions** for the model
4. **Check if key is expired** or needs regeneration

### Error: HTTP 404 Not Found

```
RuntimeError: Generic API HTTP error: 404
```

**Solution:** Check API URL and model name:

1. **Verify URL ends with `/v1`** or correct version
2. **Check model name is valid** for that service
3. **Some services require full paths** (e.g., Azure):
   ```yaml
   azure:
     api_url: https://YOUR-RESOURCE.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT
   ```

### Error: Model not found

```
RuntimeError: Generic API error: model not available
```

**Solution:** Verify model name for your service:

- **OpenRouter:** Use format `provider/model-name`
  ```yaml
  model: meta-llama/llama-3.1-70b-instruct
  ```

- **Groq:** Use exact model ID from their docs
  ```yaml
  model: llama-3.1-70b-versatile
  ```

- **LiteLLM:** Use `model_name` from litellm_config.yaml
  ```yaml
  model: gpt-4  # Model name from LiteLLM config
  ```

- **Azure:** Use your deployment name
  ```yaml
  model: gpt-4  # Your Azure deployment name
  ```

### Error: Connection timeout

```
httpx.ConnectTimeout: [Errno 110] Connection timed out
```

**Solution:**

1. **Check network connectivity** to the API endpoint
2. **Verify the API URL** is correct and accessible
3. **Check firewall rules** if using corporate network
4. **Increase timeout** if needed:
   ```python
   # In provider client code
   timeout=300.0  # 5 minutes
   ```

### Error: Rate limit exceeded

```
RuntimeError: Generic API HTTP error: 429
```

**Solution:**

1. **Wait and retry** - most services have per-minute limits
2. **Check your usage** in the service dashboard
3. **Consider upgrading** your plan if consistently hitting limits
4. **Implement retry logic** in your configuration

### Error: Invalid request format

```
RuntimeError: Generic API error: invalid request
```

**Solution:**

1. **Check request format** - ensure it matches OpenAI format
2. **Verify headers** are correctly formatted
3. **Check model parameters** (temperature, max_tokens, etc.)
4. **Test with simpler request** to isolate the issue

## Performance Issues

### Slow Response Times

If API is slow:

```yaml
generic:
  client: generic_client
  model: your-model
  temperature: 0.2
  api_url: https://your-service.com/v1
  # Consider faster models or services
```

**Performance Tips:**

- **Groq is very fast** (optimized inference)
- **Smaller models respond faster** than larger ones
- **Use dedicated providers** for better performance
- **Consider regional endpoints** if available

### High Latency

**Solutions:**

1. **Use services with regional endpoints** closer to your location
2. **Enable caching** where possible
3. **Use faster models** for time-sensitive applications
4. **Implement request batching** if supported

## Debugging Techniques

### Enable Verbose Logging

Check the run logs for detailed information:

```bash
# Check the latest run log
tail -f runs/$(date +%Y-%m-%d)/run.log

# Check specific provider logs
grep "generic" runs/$(date +%Y-%m-%d)/run.log
```

### Test API Endpoint Directly

Test the API endpoint with curl:

```bash
# Test OpenRouter endpoint
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "meta-llama/llama-3.1-70b-instruct",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Check Configuration Loading

Verify that your configuration is being loaded correctly:

```bash
# Test configuration loading
./index.py --provider generic --dry-run --verbose
```

## Common Issues and Solutions

### Headers Not Working

**Problem:** Custom headers are not being sent or recognized.

**Solution:** Check that your provider client supports custom headers. Currently supported:
- `grok_client.py` ✅
- Other clients may need updates

### Authentication Errors

**Problem:** API returns authentication errors despite correct keys.

**Solution:**
1. Verify your API keys in `.env`
2. Check Portkey virtual key is correct
3. Ensure headers are formatted correctly
4. Check if service requires additional authentication

### Timeout Issues

**Problem:** Requests timeout when using slow proxies.

**Solution:** Increase timeout in provider client:

```python
# In provider client code:
timeout=300.0  # 5 minutes
```

### Model Output Quality

**Problem:** Model outputs are poor quality or irrelevant.

**Solution:**
1. **Adjust temperature** (lower for more focused, higher for creative)
2. **Try different models** with better performance
3. **Check prompt formatting** and instructions
4. **Verify input data quality** and relevance

## Testing Checklist

Before using a new generic provider configuration:

- [ ] **Configuration loads** without errors
- [ ] **API endpoint is accessible** and responsive
- [ ] **Authentication works** with provided keys
- [ ] **Model is available** and accessible
- [ ] **Request format is correct** for the service
- [ ] **Response format is parsed** correctly
- [ ] **Output quality meets** expectations
- [ ] **Performance is acceptable** for your use case

## See Also

- [Generic Provider Quick Start](GENERIC_PROVIDER_QUICKSTART.md) - Basic setup
- [Generic Provider Services](GENERIC_PROVIDER_SERVICES.md) - Service-specific configurations
- [Generic Provider Advanced](GENERIC_PROVIDER_ADVANCED.md) - Advanced configurations
- [Generic Provider Best Practices](GENERIC_PROVIDER_BEST_PRACTICES.md) - Best practices