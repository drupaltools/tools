"""Google Gemini client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any


def generate_summary(
    prompt: str,
    model: str = "gemini-1.5-pro",
    temperature: float = 0.2,
    api_url: str = None,
    headers: Dict[str, str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using Google Gemini API.

    Args:
        prompt: Prompt text
        model: Model name
        temperature: Temperature setting
        api_url: Optional custom API URL (limited SDK support)
        headers: Optional custom headers (limited SDK support)
        **kwargs: Additional parameters

    Note:
        Google Generative AI SDK has limited support for custom URLs/headers.
        The SDK uses genai.configure() which doesn't easily support custom endpoints.
        Consider using httpx directly if you need full proxy support.

    Returns:
        dict with 'text', 'tokens', and 'model' keys
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai>=0.7")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set in environment")

    # Note: Google Generative AI SDK doesn't directly support custom base URLs
    # The genai.configure() method primarily handles API key setup
    if api_url:
        print(f"Warning: Gemini SDK has limited support for custom API URLs")
        # Custom URLs may not work with the official SDK

    if headers:
        print(f"Warning: Gemini SDK has limited support for custom headers")
        # Custom headers may not work with the official SDK

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
