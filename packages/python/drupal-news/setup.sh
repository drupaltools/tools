#!/usr/bin/env bash

set -euo pipefail

echo "======================================"
echo "Drupal News Aggregator Setup"
echo "======================================"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required but not installed."
  exit 1
fi

if [ ! -f "pyproject.toml" ]; then
  echo "Error: run this script from packages/python/drupal-news/"
  exit 1
fi

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading packaging tools..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing drupal-news in editable mode with dev extras..."
python -m pip install -e ".[dev]"

echo
echo "Setup complete."
echo
echo "Useful commands:"
echo "  source venv/bin/activate"
echo "  drupal-news --dry-run"
echo "  python3 index.py --dry-run"
echo
echo "Optional AI provider extras:"
echo "  python -m pip install -e '.[openai]'"
echo "  python -m pip install -e '.[anthropic]'"
echo "  python -m pip install -e '.[google]'"
echo "  python -m pip install -e '.[qwen]'"
echo "  python -m pip install -e '.[grok]'"
echo "  python -m pip install -e '.[deepseek]'"
echo "  python -m pip install -e '.[all-providers]'"
echo
echo "Deactivate when finished with: deactivate"
