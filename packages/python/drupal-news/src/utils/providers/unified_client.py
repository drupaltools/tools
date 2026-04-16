"""Unified AI client for Drupal Aggregator.

This client can handle all major AI providers through a unified interface:
- OpenAI and OpenAI-compatible APIs (OpenRouter, Together AI, Groq, etc.)
- Anthropic Claude
- Google Gemini
- Alibaba Qwen/DashScope
- Ollama
- LM Studio
- DeepSeek
- xAI Grok
"""

import os
import httpx
from typing import Dict, Any, Optional
import importlib

def generate_summary(
    prompt: str,
    model: str,
    provider: str = "generic",
    temperature: float = 0.2,
    api_url: str = None,
    headers: Dict[str, str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using any supported AI provider through a unified interface.

    Args:
        prompt: Prompt text
        model: Model name
        provider: Provider name (openai, anthropic, gemini, ollama, lmstudio, qwen, grok, deepseek, generic)
        temperature: Temperature setting (0.0 to 1.0)
        api_url: Optional custom API URL
        headers: Optional custom headers
        **kwargs: Additional parameters (max_tokens, etc.)

    Returns:
        dict with 'text', 'tokens', 'model', 'provider' keys

    Examples:
        # OpenAI
        generate_summary(prompt, "gpt-4.1-mini", "openai")

        # Anthropic Claude
        generate_summary(prompt, "claude-3-5-sonnet-20241022", "anthropic")

        # Google Gemini
        generate_summary(prompt, "gemini-1.5-pro", "gemini")

        # Generic OpenAI-compatible (OpenRouter, Together AI, etc.)
        generate_summary(
            prompt,
            "meta-llama/llama-3.1-70b-instruct",
            "generic",
            api_url="https://openrouter.ai/api/v1",
            headers={"Authorization": "Bearer sk-or-..."}
        )
    """

    # Handle provider-specific logic
    if provider == "openai":
        return _generate_openai_summary(prompt, model, temperature, api_url, headers, **kwargs)
    elif provider == "anthropic":
        return _generate_anthropic_summary(prompt, model, temperature, api_url, headers, **kwargs)
    elif provider == "gemini":
        return _generate_gemini_summary(prompt, model, temperature, api_url, headers, **kwargs)
    elif provider == "qwen":
        return _generate_qwen_summary(prompt, model, temperature, api_url, headers, **kwargs)
    elif provider in ["ollama", "lmstudio"]:
        return _generate_http_summary(prompt, model, provider, temperature, api_url, headers, **kwargs)
    elif provider == "grok":
        return _generate_xai_summary(prompt, model, temperature, api_url, headers, **kwargs)
    elif provider == "deepseek":
        return _generate_deepseek_summary(prompt, model, temperature, api_url, headers, **kwargs)
    elif provider == "zai":
        return _generate_anthropic_summary(prompt, model, temperature, api_url, headers, **kwargs, api_key_env="ZAI_API_KEY", provider_name="zai")
    elif provider == "minimax":
        return _generate_anthropic_summary(prompt, model, temperature, api_url, headers, **kwargs, api_key_env="MINIMAX_API_KEY", provider_name="minimax")
    else:
        # Default to generic OpenAI-compatible client
        return _generate_generic_summary(prompt, model, temperature, api_url, headers, **kwargs)

def _generate_openai_summary(prompt: str, model: str, temperature: float, api_url: str = None,
                           headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
    """Generate summary using OpenAI API."""
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

def _generate_anthropic_summary(prompt: str, model: str, temperature: float, api_url: str = None,
                              headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
    """Generate summary using Anthropic API."""
    try:
        import anthropic
    except ImportError:
        raise ImportError("Anthropic package not installed. Install with: pip install anthropic>=0.34")

    # Get API key from environment (supports custom providers)
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

def _generate_gemini_summary(prompt: str, model: str, temperature: float, api_url: str = None,
                           headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
    """Generate summary using Google Gemini API."""
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai>=0.7")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set in environment")

    # Note: Google Generative AI SDK doesn't directly support custom base URLs
    if api_url:
        print(f"Warning: Gemini SDK has limited support for custom API URLs")

    if headers:
        print(f"Warning: Gemini SDK has limited support for custom headers")

    genai.configure(api_key=api_key)

    try:
        model_obj = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": kwargs.get("max_tokens", 4000),
            }
        )

        system_prompt = "You are a technical writer specializing in Drupal documentation."
        full_prompt = f"{system_prompt}\n\n{prompt}"

        response = model_obj.generate_content(full_prompt)

        # Estimate tokens (Gemini doesn't always provide exact counts)
        tokens = kwargs.get("estimated_tokens", len(prompt.split()) * 1.3)

        return {
            "text": response.text,
            "tokens": int(tokens),
            "model": model,
            "provider": "gemini"
        }
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {str(e)}")

def _generate_qwen_summary(prompt: str, model: str, temperature: float, api_url: str = None,
                         headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
    """Generate summary using Qwen/DashScope API."""
    try:
        import dashscope
        from dashscope import Generation
    except ImportError:
        raise ImportError("DashScope package not installed. Install with: pip install dashscope>=1.17")

    api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("QWEN_API_KEY or DASHSCOPE_API_KEY not set in environment")

    dashscope.api_key = api_key

    # Note: DashScope SDK doesn't directly support custom base_url
    if api_url:
        print(f"Warning: Qwen/DashScope SDK has limited support for custom API URLs")

    try:
        system_prompt = "You are a technical writer specializing in Drupal documentation."

        response = Generation.call(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            result_format='message'
        )

        if response.status_code == 200:
            text = response.output.choices[0].message.content
            tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0

            # Estimate if not provided
            if tokens == 0:
                tokens = len(prompt.split()) + len(text.split())

            return {
                "text": text,
                "tokens": tokens,
                "model": model,
                "provider": "qwen"
            }
        else:
            raise RuntimeError(f"Qwen API error: {response.message}")
    except Exception as e:
        raise RuntimeError(f"Qwen API error: {str(e)}")

def _generate_http_summary(prompt: str, model: str, provider: str, temperature: float,
                         api_url: str = None, headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
    """Generate summary using HTTP-based APIs (Ollama, LM Studio)."""

    # Default URLs for local services
    if not api_url:
        if provider == "ollama":
            api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        elif provider == "lmstudio":
            api_url = os.getenv("LMSTUDIO_API_URL", "http://localhost:1234")

    base_url = api_url.rstrip("/")

    # Build headers
    request_headers = {
        "Content-Type": "application/json"
    }

    # Add optional headers
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
                f"{base_url}/v1/chat/completions",
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
            "provider": provider
        }
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"{provider.capitalize()} API HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise RuntimeError(f"{provider.capitalize()} API request error: {str(e)}")
    except KeyError as e:
        raise RuntimeError(f"{provider.capitalize()} API unexpected response format: missing {str(e)}")
    except Exception as e:
        raise RuntimeError(f"{provider.capitalize()} API error: {str(e)}")

def _generate_xai_summary(prompt: str, model: str, temperature: float, api_url: str = None,
                        headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
    """Generate summary using xAI Grok API."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY not set in environment")

    base_url = api_url if api_url else "https://api.x.ai/v1"

    # Build headers
    request_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
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

        return {
            "text": text,
            "tokens": total_tokens,
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "model": model,
            "provider": "grok"
        }
    except httpx.HTTPError as e:
        raise RuntimeError(f"xAI API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"xAI error: {str(e)}")

def _generate_deepseek_summary(prompt: str, model: str, temperature: float, api_url: str = None,
                             headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
    """Generate summary using DeepSeek API."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set in environment")

    base_url = api_url if api_url else "https://api.deepseek.com"

    # Build headers
    request_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
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

        return {
            "text": text,
            "tokens": total_tokens,
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "model": model,
            "provider": "deepseek"
        }
    except httpx.HTTPError as e:
        raise RuntimeError(f"DeepSeek API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"DeepSeek error: {str(e)}")

def _generate_generic_summary(prompt: str, model: str, temperature: float, api_url: str = None,
                            headers: Dict[str, str] = None, **kwargs) -> Dict[str, Any]:
    """Generate summary using any OpenAI-compatible API endpoint."""
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