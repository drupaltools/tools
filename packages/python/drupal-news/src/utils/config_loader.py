"""Unified configuration loader for drupal_news.

This module handles loading and parsing the unified config.yml file.
All configuration (core settings, sources, AI providers, prompts, API keys)
is now consolidated in a single config.yml file.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class ConfigLoader:
    """Loads and manages unified configuration from config.yml."""

    def __init__(self, config_path: str = "config.yml"):
        """
        Initialize config loader.

        Args:
            config_path: Path to config.yml file
        """
        self.config_path = Path(config_path)
        self._config = None
        self._env_vars = {}

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from config.yml with environment variable substitution.

        Returns:
            Complete configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}\n"
                f"Copy config.example.yml to config.yml and customize it."
            )

        # Load raw YAML
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

        if not self._config:
            raise ValueError(f"Config file is empty: {self.config_path}")

        # Load environment variables
        self._load_env_vars()

        # Substitute environment variables in config
        self._config = self._substitute_env_vars(self._config)

        # Set environment variables from api_keys section
        self._set_api_keys_to_env()

        return self._config

    def _load_env_vars(self):
        """Load environment variables, including from .env file if present."""
        # First, load from actual environment
        self._env_vars = dict(os.environ)

        # Then try to load from .env file (if exists)
        env_file = Path(".env")
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue

                        # Parse KEY=value or KEY="value"
                        match = re.match(r'^([A-Z_][A-Z0-9_]*)=(.*)$', line)
                        if match:
                            key, value = match.groups()
                            # Remove quotes if present
                            value = value.strip('"').strip("'")
                            # Only set if not already in environment
                            if key not in self._env_vars:
                                self._env_vars[key] = value
            except Exception as e:
                print(f"Warning: Could not read .env file: {e}")

    def _substitute_env_vars(self, data: Any) -> Any:
        """
        Recursively substitute ${VAR_NAME} placeholders with environment variables.

        Args:
            data: Data structure to process (dict, list, str, etc.)

        Returns:
            Data with environment variables substituted
        """
        if isinstance(data, dict):
            return {k: self._substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            # Replace ${VAR_NAME} with environment variable value
            def replace_var(match):
                var_name = match.group(1)
                return self._env_vars.get(var_name, match.group(0))

            return re.sub(r'\$\{([A-Z_][A-Z0-9_]*)\}', replace_var, data)
        else:
            return data

    def _set_api_keys_to_env(self):
        """Set API keys from config to environment variables (if not already set)."""
        api_keys = self._config.get("api_keys", {})
        for key, value in api_keys.items():
            # Only set if not already in environment and value is not a placeholder
            if key not in os.environ and value and not value.startswith("${"):
                os.environ[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.

        Args:
            key_path: Dot-separated path (e.g., "core.timeframe_days")
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            config.get("ai.default_provider")  # Returns "openrouter"
            config.get("core.http.timeout_sec")  # Returns 20
        """
        if not self._config:
            self.load()

        keys = key_path.split(".")
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_core_config(self) -> Dict[str, Any]:
        """Get core configuration section."""
        return self.get("core", {})

    def get_sources_config(self) -> Dict[str, Any]:
        """Get sources configuration section."""
        return self.get("sources", {})

    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration section."""
        return self.get("ai", {})

    def get_providers_config(self) -> Dict[str, Any]:
        """
        Get providers configuration in legacy format for compatibility.

        Returns:
            Dict with 'default_provider' and 'providers' keys
        """
        ai_config = self.get_ai_config()
        return {
            "default_provider": ai_config.get("default_provider", "openrouter"),
            "providers": ai_config.get("providers", {})
        }

    def get_prompt_template(self) -> str:
        """
        Get AI prompt template.

        Returns:
            Prompt template string with placeholders
        """
        prompt = self.get("prompt", "")
        if not prompt:
            # Fallback to hardcoded default if not in config
            from drupal_news.ai_summarizer import SUMMARIZER_PROMPT_TEMPLATE
            return SUMMARIZER_PROMPT_TEMPLATE
        return prompt.strip()

    def get_provider(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific provider configuration.

        Args:
            provider_name: Name of provider (e.g., "openai", "anthropic")

        Returns:
            Provider configuration dict or None if not found
        """
        providers = self.get("ai.providers", {})
        return providers.get(provider_name)

    def get_default_provider_name(self) -> str:
        """Get default provider name."""
        return self.get("ai.default_provider", "openrouter")


# Global config instance (singleton pattern)
_config_instance = None


def get_config(config_path: str = "config.yml", force_reload: bool = False) -> ConfigLoader:
    """
    Get global config instance.

    Args:
        config_path: Path to config.yml file
        force_reload: Force reloading config from file

    Returns:
        ConfigLoader instance
    """
    global _config_instance

    if _config_instance is None or force_reload:
        _config_instance = ConfigLoader(config_path)
        _config_instance.load()

    return _config_instance


# Convenience functions for common operations
def load_config(config_path: str = "config.yml") -> Dict[str, Any]:
    """
    Load core configuration.

    Args:
        config_path: Path to config.yml file

    Returns:
        Core configuration dict merged with sources
    """
    config = get_config(config_path)
    core = config.get_core_config()
    sources = config.get_sources_config()

    # Merge core and sources
    return {
        **core,
        "sources": sources
    }


def load_providers_config(config_path: str = "config.yml") -> Dict[str, Any]:
    """
    Load providers configuration.

    Args:
        config_path: Path to config.yml file

    Returns:
        Providers configuration dict with 'default_provider' and 'providers' keys
    """
    config = get_config(config_path)
    return config.get_providers_config()


def load_prompt_template(config_path: str = "config.yml") -> str:
    """
    Load prompt template.

    Args:
        config_path: Path to config.yml file

    Returns:
        Prompt template string
    """
    config = get_config(config_path)
    return config.get_prompt_template()
