"""Tests for validator module."""
import pytest
from drupal_news.validator import validate_url, validate_item, validate_items


def test_validate_url():
    """Test URL validation."""
    assert validate_url("https://drupal.org/news") == True
    assert validate_url("http://example.com") == True
    assert validate_url("invalid-url") == False
    assert validate_url("") == False


def test_validate_item():
    """Test item validation."""
    # Valid item
    valid_item = {
        "title": "Test Title",
        "url": "https://drupal.org/test",
        "source_type": "rss"
    }
    is_valid, errors = validate_item(valid_item)
    assert is_valid == True
    assert len(errors) == 0

    # Missing title
    invalid_item = {
        "url": "https://drupal.org/test",
        "source_type": "rss"
    }
    is_valid, errors = validate_item(invalid_item)
    assert is_valid == False
    assert "Missing title" in errors

    # Invalid URL
    invalid_item = {
        "title": "Test",
        "url": "invalid",
        "source_type": "rss"
    }
    is_valid, errors = validate_item(invalid_item)
    assert is_valid == False
    assert any("Invalid URL" in e for e in errors)


def test_validate_items():
    """Test items list validation."""
    items = [
        {
            "title": "Test 1",
            "url": "https://drupal.org/1",
            "source_type": "rss"
        },
        {
            "title": "Test 2",
            "url": "https://drupal.org/2",
            "source_type": "page"
        }
    ]

    report = validate_items(items)

    assert report["rss_count"] == 1
    assert report["page_count"] == 1
    assert report["total_count"] == 2
    assert report["passed"] == True
