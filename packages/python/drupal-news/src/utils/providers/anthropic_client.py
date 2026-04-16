"""Anthropic Claude client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any


def generate_summary(
    prompt: str,
    model: str = "claude-3-5-sonnet-20241022",
    temperature: float = 0.2,
    api_url: str = None,
    headers: Dict[str, str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using Anthropic API.

    Args:
        prompt: Prompt text
        model: Model name
        temperature: Temperature setting
        api_url: Optional custom API URL (e.g., for proxies)
        headers: Optional custom headers (e.g., for Portkey)
        **kwargs: Additional parameters (api_key_env, provider_name)

    Returns:
        dict with 'text', 'tokens', 'model', and 'provider' keys
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("Anthropic package not installed. Install with: pip install anthropic>=0.34")

    # Get API key from environment (supports custom providers like z.ai and MiniMax)
    api_key_env = kwargs.get("api_key_env", "ANTHROPIC_API_KEY")
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise ValueError(f"{api_key_env} not set in environment")

    # Get provider name for return value
    provider_name = kwargs.get("provider_name", "anthropic")

    # Build client with optional custom URL and headers
    client_kwargs = {"api_key": api_key}

    if api_url:
        client_kwargs["base_url"] = api_url

    if headers:
        client_kwargs["default_headers"] = headers

    client = anthropic.Anthropic(**client_kwargs)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=kwargs.get("max_tokens", 4000),
            temperature=temperature,
            system="You are a technical writer specializing in Drupal documentation.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        input_tokens = getattr(response.usage, "input_tokens", 0)
        output_tokens = getattr(response.usage, "output_tokens", 0)
        total_tokens = (input_tokens or 0) + (output_tokens or 0)

        return {
            "text": response.content[0].text,
            "tokens": total_tokens,
            "input_tokens": input_tokens or None,
            "output_tokens": output_tokens or None,
            "model": model,
            "provider": provider_name
        }
    except Exception as e:
        raise RuntimeError(f"Anthropic API error: {str(e)}")
