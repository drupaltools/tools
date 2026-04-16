"""Generic OpenAI-compatible client for any API endpoint.

This client works with any service that implements the OpenAI chat completions API format,
including OpenRouter, Together AI, Perplexity, Groq, and custom endpoints.
"""
import os
import httpx
from typing import Dict, Any


def generate_summary(
    prompt: str,
    model: str,
    temperature: float = 0.2,
    api_url: str = None,
    headers: Dict[str, str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using any OpenAI-compatible API endpoint.

    Args:
        prompt: The prompt text to send
        model: Model identifier (e.g., "meta-llama/llama-3.1-70b-instruct")
        temperature: Temperature setting (0.0 to 1.0)
        api_url: Base API URL (e.g., "https://api.together.xyz/v1")
        headers: Custom headers (typically authentication)
        **kwargs: Additional parameters

    Environment Variables:
        GENERIC_API_KEY: API key for authentication (optional if provided in headers)
        GENERIC_API_URL: Default API URL if not provided in call

    Returns:
        dict with 'text', 'tokens', 'model', and 'provider' keys

    Examples:
        # OpenRouter
        generate_summary(
            prompt="...",
            model="meta-llama/llama-3.1-70b-instruct",
            api_url="https://openrouter.ai/api/v1",
            headers={"Authorization": "Bearer sk-or-..."}
        )

        # Together AI
        generate_summary(
            prompt="...",
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            api_url="https://api.together.xyz/v1",
            headers={"Authorization": "Bearer ..."}
        )

        # Groq
        generate_summary(
            prompt="...",
            model="llama-3.1-70b-versatile",
            api_url="https://api.groq.com/openai/v1",
            headers={"Authorization": "Bearer gsk_..."}
        )
    """
    # Get API URL from parameter, environment, or error
    base_url = api_url or os.getenv("GENERIC_API_URL")
    if not base_url:
        raise ValueError(
            "API URL required. Provide via api_url parameter or GENERIC_API_URL environment variable."
        )

    # Remove trailing slash if present
    base_url = base_url.rstrip("/")

    # Build headers
    request_headers = {
        "Content-Type": "application/json"
    }

    # Add API key from environment if available (and not already in custom headers)
    api_key = os.getenv("GENERIC_API_KEY")
    if api_key and (not headers or "Authorization" not in headers):
        request_headers["Authorization"] = f"Bearer {api_key}"

    # Merge custom headers (custom headers override defaults)
    if headers:
        request_headers.update(headers)

    # Build request payload
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a technical writer specializing in Drupal documentation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature,
        "max_tokens": kwargs.get("max_tokens", 4000)
    }

    try:
        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers=request_headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        # Extract response
        summary_text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        total_tokens = usage.get("total_tokens")
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")

        if total_tokens is None:
            total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

        return {
            "text": summary_text,
            "tokens": total_tokens or 0,
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "model": model,
            "provider": "generic"
        }

    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Generic API HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise RuntimeError(f"Generic API request error: {str(e)}")
    except KeyError as e:
        raise RuntimeError(f"Generic API unexpected response format: missing {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Generic API error: {str(e)}")
