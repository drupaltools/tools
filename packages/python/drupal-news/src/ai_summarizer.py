"""AI summarizer for Drupal Newsletter."""
import importlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import time
from drupal_news.output_formatter import items_to_text


SUMMARIZER_PROMPT_TEMPLATE = """
You are a technical writer for the Drupal community. Generate a summary of Drupal news and updates.

**Requirements:**
1. Focus on AI module and news on AI
2. Each fact MUST include a [source](URL) link
3. Use clear, factual language - no hype
4. If no major updates: include "No significant core updates this week"
5. Present RSS/new modules as a table with columns: URL, Name, Description
6. Organize by sections: Core Updates, Modules, AI/Automation, Canvas/Admin UI, Planet, D.O. Blog

**Timeframe:** Last {timeframe_days} days ({timezone})

**Items to summarize:**

{items_text}

Generate the summary in Markdown format with proper sections and source links.
"""


def load_prompt_template(prompt_file: str = None) -> str:
    """
    Load prompt template from config.yml or use default.

    Priority:
    1. Specified prompt_file parameter (for testing/overrides)
    2. config.yml prompt section
    3. Hardcoded default (fallback)

    Args:
        prompt_file: Path to prompt file (optional, overrides config)

    Returns:
        Prompt template string with placeholders
    """
    # If specific file provided, try to use it
    if prompt_file is not None:
        prompt_path = Path(prompt_file)
        if prompt_path.exists():
            try:
                return prompt_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"Warning: Could not read {prompt_file}: {e}")

    # Load from unified config.yml
    try:
        from drupal_news.utils.config_loader import get_config
        config = get_config("config.yml")
        prompt = config.get_prompt_template()
        if prompt:
            return prompt
    except Exception as e:
        print(f"Warning: Could not load prompt from config.yml: {e}")

    # Fall back to hardcoded default
    print("Using default hardcoded prompt template")
    return SUMMARIZER_PROMPT_TEMPLATE


def get_provider_client(provider_name: str, client_name: str = None):
    """
    Dynamically load provider client module.

    Args:
        provider_name: Provider name (e.g., 'openai', 'anthropic')
        client_name: Optional client name from config (e.g., 'generic_client')

    Returns:
        Provider client module
    """
    try:
        # Use unified client for all providers
        module = importlib.import_module(f"drupal_news.utils.providers.unified_client")
        return module
    except ImportError as e:
        # Fallback to specific provider clients if unified client not available
        try:
            # Use client_name if provided, otherwise use provider_name
            module_name = client_name if client_name else f"{provider_name}_client"
            # Remove _client suffix if already present
            if not module_name.endswith('_client'):
                module_name = f"{module_name}_client"
            module = importlib.import_module(f"drupal_news.utils.providers.{module_name}")
            return module
        except ImportError:
            raise ImportError(f"Provider '{provider_name}' (client: {client_name or provider_name}) not found: {e}")



def calculate_cost(provider: str, provider_config: Dict[str, Any], summary_result: Dict[str, Any]) -> float:
    """Estimate USD cost for a summary run based on token usage and configured pricing."""
    if not provider_config:
        return 0.0

    pricing = provider_config.get("pricing")
    if not pricing:
        return 0.0

    input_tokens = summary_result.get("input_tokens")
    output_tokens = summary_result.get("output_tokens")
    total_tokens = summary_result.get("tokens", 0) or 0

    cost = 0.0

    input_rate = pricing.get("input_cost_per_1k")
    output_rate = pricing.get("output_cost_per_1k")
    blended_rate = pricing.get("per_1k_tokens")

    if input_tokens is not None and input_rate is not None:
        cost += (input_tokens / 1000.0) * float(input_rate)

    if output_tokens is not None and output_rate is not None:
        cost += (output_tokens / 1000.0) * float(output_rate)

    # Fallback to blended pricing when detailed usage is absent
    if cost == 0.0 and blended_rate is not None:
        cost += (total_tokens / 1000.0) * float(blended_rate)

    return round(cost, 6)



def summarize(
    items: List[Dict[str, Any]],
    provider: str,
    model: str,
    temperature: float,
    timeframe_days: int,
    timezone: str,
    max_items: int = 200,
    chunk_size: int = 200,
    provider_config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate AI summary of items.

    Args:
        items: List of news items
        provider: AI provider name
        model: Model name
        temperature: Temperature setting
        timeframe_days: Number of days covered
        timezone: Timezone name
        max_items: Maximum items to process
        chunk_size: Chunk size for large inputs
        provider_config: Full provider configuration (includes api_url, headers, etc.)

    Returns:
        Dictionary with 'text', 'tokens', 'model', 'provider', 'duration'
    """
    start_time = time.time()

    # Load provider client
    # Extract client name from provider_config if available
    client_name = provider_config.get("client") if provider_config else None
    client = get_provider_client(provider, client_name)

    # Convert items to text
    items_text = items_to_text(items, max_items)

    # Load prompt template from file or use default
    template = load_prompt_template()

    def render_prompt(items_text_value: str) -> str:
        return template.format(
            timeframe_days=timeframe_days,
            timezone=timezone,
            items_text=items_text_value
        )

    prompt = render_prompt(items_text)

    # Prepare kwargs for provider (prompt injected per request)
    base_kwargs = {
        "model": model,
        "provider": provider,  # Pass provider to unified client
        "temperature": temperature
    }

    # Add optional provider-specific settings
    if provider_config:
        if "api_url" in provider_config:
            base_kwargs["api_url"] = provider_config["api_url"]
        if "headers" in provider_config:
            base_kwargs["headers"] = provider_config["headers"]

    # Check if chunking needed
    if len(items) > chunk_size:
        summary_result = _summarize_chunked(
            client,
            items,
            render_prompt,
            chunk_size,
            base_kwargs,
            provider
        )
    else:
        request_kwargs = dict(base_kwargs)
        request_kwargs["prompt"] = prompt
        try:
            # For unified client, we pass the provider as a parameter
            summary_result = client.generate_summary(**request_kwargs)
        except Exception as e:
            raise RuntimeError(f"Summarization failed: {str(e)}")

    # Add metadata
    summary_result.setdefault("provider", provider)
    summary_result.setdefault("model", model)
    summary_result["duration"] = time.time() - start_time
    summary_result["cost"] = calculate_cost(provider, provider_config or {}, summary_result)

    return summary_result


def _summarize_chunked(
    client,
    items: List[Dict[str, Any]],
    render_prompt,
    chunk_size: int,
    base_kwargs: Dict[str, Any],
    provider: str
) -> Dict[str, Any]:
    """Summarize items in chunks for large datasets."""
    summaries = []
    total_tokens = 0
    total_input_tokens = 0
    total_output_tokens = 0

    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        chunk_kwargs = dict(base_kwargs)
        chunk_kwargs["prompt"] = render_prompt(items_to_text(chunk))

        try:
            result = client.generate_summary(**chunk_kwargs)
            summaries.append(result.get("text", ""))
            total_tokens += result.get("tokens", 0) or 0
            total_input_tokens += result.get("input_tokens") or 0
            total_output_tokens += result.get("output_tokens") or 0
        except Exception as e:
            print(f"Warning: Chunk {i // chunk_size + 1} failed: {e}")

    combined_text = "\n\n".join(filter(None, summaries))

    summary = {
        "text": combined_text,
        "tokens": total_tokens,
        "model": base_kwargs.get("model"),
        "provider": provider,  # Use the provider parameter instead of extracting from client name
        "chunked": True
    }

    if total_input_tokens:
        summary["input_tokens"] = total_input_tokens
    if total_output_tokens:
        summary["output_tokens"] = total_output_tokens

    return summary


def summarize_with_fallback(
    items: List[Dict[str, Any]],
    providers_config: Dict[str, Any],
    default_provider: str,
    timeframe_days: int,
    timezone: str,
    fallback_order: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Summarize with automatic fallback to other providers.

    Args:
        items: List of news items
        providers_config: Providers configuration
        default_provider: Default provider to try first
        timeframe_days: Days covered
        timezone: Timezone name
        fallback_order: Optional custom fallback order

    Returns:
        Summary result with provider info
    """
    if fallback_order is None:
        fallback_order = ["openai", "anthropic", "ollama", "qwen", "openrouter"]

    # Try default provider first
    provider_list = [default_provider] + [p for p in fallback_order if p != default_provider]

    last_error = None

    for provider_name in provider_list:
        provider_config = providers_config.get("providers", {}).get(provider_name)

        if not provider_config:
            continue

        try:
            result = summarize(
                items=items,
                provider=provider_name,
                model=provider_config["model"],
                temperature=provider_config.get("temperature", 0.2),
                timeframe_days=timeframe_days,
                timezone=timezone,
                provider_config=provider_config
            )

            return result

        except Exception as e:
            last_error = e
            print(f"Provider {provider_name} failed: {e}")
            continue

    # All providers failed
    raise RuntimeError(f"All providers failed. Last error: {last_error}")


def generate_placeholder_summary(items: List[Dict[str, Any]], timeframe_days: int) -> str:
    """
    Generate placeholder summary for dry-run mode.

    Args:
        items: List of items
        timeframe_days: Days covered

    Returns:
        Placeholder markdown summary
    """
    return f"""# Drupal Newsletter Summary (Dry Run)

**Timeframe:** Last {timeframe_days} days

## Summary

This is a placeholder summary for dry-run mode.
Total items collected: {len(items)}

### Core Updates
No significant core updates this week.

### New Modules
{len([i for i in items if i.get('source_type') == 'rss'])} new modules found.

### AI and Automation
No major AI updates this week.

---
*This is a dry-run summary. Enable AI provider for actual summaries.*
"""
