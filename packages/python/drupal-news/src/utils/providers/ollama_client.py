"""Ollama client for Drupal Aggregator."""
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
    Generate summary using Ollama local API.

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
    base_url = api_url if api_url else os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Build headers
    request_headers = {}
    if headers:
        request_headers.update(headers)

    try:
        system_prompt = "You are a technical writer specializing in Drupal documentation."

        response = httpx.post(
            f"{base_url}/api/generate",
            headers=request_headers if request_headers else None,
            json={
                "model": model,
                "prompt": f"{system_prompt}\n\n{prompt}",
                "temperature": temperature,
                "stream": False
            },
            timeout=120.0
        )
        response.raise_for_status()

        data = response.json()
        text = data.get("response", "")

        # Estimate tokens
        tokens = len(prompt.split()) + len(text.split())

        return {
            "text": text,
            "tokens": tokens,
            "model": model,
            "provider": "ollama"
        }
    except httpx.HTTPError as e:
        raise RuntimeError(f"Ollama API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {str(e)}")
