"""Tests for timebox utilities."""
import pytest
from datetime import datetime
from drupal_news.utils.consolidated_utils import get_timezone, now_in_tz, days_ago, parse_date


def test_get_timezone():
    """Test timezone retrieval."""
    tz = get_timezone("Europe/Athens")
    assert tz is not None
    assert str(tz) == "Europe/Athens"


def test_now_in_tz():
    """Test current time in timezone."""
    now = now_in_tz("Europe/Athens")
    assert isinstance(now, datetime)
    assert now.tzinfo is not None


def test_days_ago():
    """Test days_ago calculation."""
    past = days_ago(7, "Europe/Athens")
    now = now_in_tz("Europe/Athens")

    assert past < now
    diff = now - past
    assert diff.days == 7


def test_parse_date():
    """Test date parsing."""
    # ISO format
    dt = parse_date("2025-10-24T10:00:00Z")
    assert dt is not None
    assert dt.year == 2025
    assert dt.month == 10
    assert dt.day == 24

    # Invalid date
    dt = parse_date("invalid-date")
    assert dt is None
