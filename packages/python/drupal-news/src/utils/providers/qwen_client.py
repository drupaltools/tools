"""Qwen (Alibaba Cloud) client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any


def generate_summary(
    prompt: str,
    model: str = "qwen2.5-7b-chat",
    temperature: float = 0.2,
    api_url: str = None,
    headers: Dict[str, str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using Qwen API via DashScope.

    Args:
        prompt: Prompt text
        model: Model name
        temperature: Temperature setting
        api_url: Optional custom API URL (may not work with DashScope SDK)
        headers: Optional custom headers (may not work with DashScope SDK)
        **kwargs: Additional parameters

    Note:
        DashScope SDK has limited support for custom URLs/headers.
        Consider using httpx directly if you need full proxy support.

    Returns:
        dict with 'text', 'tokens', and 'model' keys
    """
    try:
        import dashscope
        from dashscope import Generation
    except ImportError:
        raise ImportError("DashScope package not installed. Install with: pip install dashscope>=1.17")

    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        raise ValueError("QWEN_API_KEY not set in environment")

    dashscope.api_key = api_key

    # Note: DashScope SDK doesn't directly support custom base_url
    # If you need proxy support, consider using httpx with OpenAI-compatible endpoint
    if api_url:
        print(f"Warning: Qwen/DashScope SDK has limited support for custom API URLs")
        # You might need to use dashscope.base_http_api_url if available

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
