"""Grok (xAI) client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any
import httpx


def generate_summary(
    prompt: str,
    model: str = "grok-beta",
    temperature: float = 0.2,
    api_url: str = None,
    headers: Dict[str, str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using Grok API (OpenAI compatible).

    Args:
        prompt: Prompt text
        model: Model name
        temperature: Temperature setting
        api_url: Optional custom API URL (e.g., for Portkey proxy)
        headers: Optional custom headers (e.g., Portkey auth headers)
        **kwargs: Additional parameters

    Returns:
        dict with 'text', 'tokens', and 'model' keys
    """
    api_key = os.getenv("GROK_API_KEY")
    if not api_key:
        raise ValueError("GROK_API_KEY not set in environment")

    # Use custom URL if provided, otherwise default
    base_url = api_url if api_url else "https://api.x.ai/v1"

    # Build headers
    request_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Add custom headers if provided (e.g., for Portkey)
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
        tokens = data.get("usage", {}).get("total_tokens", 0)

        # Estimate if not provided
        if tokens == 0:
            tokens = len(prompt.split()) + len(text.split())

        return {
            "text": text,
            "tokens": tokens,
            "model": model,
            "provider": "grok"
        }
    except httpx.HTTPError as e:
        raise RuntimeError(f"Grok API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Grok error: {str(e)}")
