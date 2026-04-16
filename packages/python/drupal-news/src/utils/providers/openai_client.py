"""OpenAI client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any


def generate_summary(
    prompt: str,
    model: str = "gpt-4.1-mini",
    temperature: float = 0.2,
    api_url: str = None,
    headers: Dict[str, str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using OpenAI API.

    Args:
        prompt: Prompt text
        model: Model name
        temperature: Temperature setting
        api_url: Optional custom API URL (e.g., for proxies)
        headers: Optional custom headers (e.g., for Portkey)
        **kwargs: Additional parameters

    Returns:
        dict with 'text', 'tokens', and 'model' keys
    """
    try:
        import openai
    except ImportError:
        raise ImportError("OpenAI package not installed. Install with: pip install openai>=1.45")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    # Build client with optional custom URL and headers
    client_kwargs = {"api_key": api_key}

    if api_url:
        client_kwargs["base_url"] = api_url

    if headers:
        client_kwargs["default_headers"] = headers

    client = openai.OpenAI(**client_kwargs)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a technical writer specializing in Drupal documentation."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=kwargs.get("max_tokens", 4000)
        )

        prompt_tokens = getattr(response.usage, "prompt_tokens", 0)
        completion_tokens = getattr(response.usage, "completion_tokens", 0)
        total_tokens = getattr(response.usage, "total_tokens", prompt_tokens + completion_tokens)

        return {
            "text": response.choices[0].message.content,
            "tokens": total_tokens,
            "input_tokens": prompt_tokens or None,
            "output_tokens": completion_tokens or None,
            "model": model,
            "provider": "openai"
        }
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
