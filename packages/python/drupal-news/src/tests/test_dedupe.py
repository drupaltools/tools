"""Tests for deduplication utilities."""
import pytest
from drupal_news.utils.consolidated_utils import dedupe_items, dedupe_by_url


def test_dedupe_items():
    """Test item deduplication."""
    items = [
        {"title": "Test 1", "url": "https://example.com/1"},
        {"title": "Test 1", "url": "https://example.com/1"},  # Duplicate
        {"title": "Test 2", "url": "https://example.com/2"},
    ]

    unique = dedupe_items(items)
    assert len(unique) == 2
    assert unique[0]["title"] == "Test 1"
    assert unique[1]["title"] == "Test 2"


def test_dedupe_by_url():
    """Test URL-based deduplication."""
    items = [
        {"title": "Title A", "url": "https://example.com/1"},
        {"title": "Title B", "url": "https://example.com/1"},  # Same URL, different title
        {"title": "Title C", "url": "https://example.com/2"},
    ]

    unique = dedupe_by_url(items)
    assert len(unique) == 2
    assert unique[0]["url"] == "https://example.com/1"
    assert unique[1]["url"] == "https://example.com/2"
