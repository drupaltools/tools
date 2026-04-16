"""LM Studio client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any
import httpx


def generate_summary(
    prompt: str,
    model: str = "qwen2.5:7b-instruct",
    temperature: float = 0.2,
    api_url: str = None,
    headers: Dict[str, str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using LM Studio local API (OpenAI compatible).

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
    base_url = api_url if api_url else os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234")

    # Build headers
    request_headers = {}
    if headers:
        request_headers.update(headers)

    try:
        response = httpx.post(
            f"{base_url}/v1/chat/completions",
            headers=request_headers if request_headers else None,
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
            "provider": "lmstudio"
        }
    except httpx.HTTPError as e:
        raise RuntimeError(f"LM Studio API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"LM Studio error: {str(e)}")
