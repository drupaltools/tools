"""OpenRouter client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any
import httpx


def generate_summary(
    prompt: str,
    model: str = "meta-llama/llama-3.1-8b-instruct",
    temperature: float = 0.2,
    api_url: str = None,
    headers: Dict[str, str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using OpenRouter API.

    Args:
        prompt: Prompt text
        model: Model name
        temperature: Temperature setting
        api_url: Optional custom API URL
        headers: Optional custom headers
        **kwargs: Additional parameters

    Returns:
        dict with 'text', 'tokens', and 'model' keys
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in environment")

    base_url = api_url if api_url else "https://openrouter.ai/api/v1"

    # Build headers
    request_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/drupaltools/tools",
        "X-Title": "Drupal News Aggregator"
    }

    if headers:
        request_headers.update(headers)

    try:
        response = httpx.post(
            f"{base_url}/chat/completions",
            headers=request_headers,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a technical writer specializing in Drupal documentation."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": kwargs.get("max_tokens", 4000)
            },
            timeout=120.0
        )
        response.raise_for_status()

        data = response.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        total_tokens = usage.get("total_tokens")
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")

        if total_tokens is None:
            total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

        # Estimate if usage not provided
        if not total_tokens:
            total_tokens = len(prompt.split()) + len(text.split())

        return {
            "text": text,
            "tokens": total_tokens,
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "model": model,
            "provider": "openrouter"
        }
    except httpx.HTTPError as e:
        raise RuntimeError(f"OpenRouter API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"OpenRouter error: {str(e)}")
