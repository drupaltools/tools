"""Consolidated utilities for Drupal Aggregator.

This module combines several smaller utility modules into a single file to reduce codebase size.
"""

import hashlib
import json
import os
import re
import pytz
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set, List, Union
from pathlib import Path
from dateutil import parser as date_parser
from bs4 import BeautifulSoup, NavigableString
from readability import Document
import yaml


# Time and timezone utilities
def get_timezone(tz_name: str = "Europe/Athens") -> pytz.tzinfo.BaseTzInfo:
    """Get timezone object."""
    return pytz.timezone(tz_name)


def now_in_tz(tz_name: str = "Europe/Athens") -> datetime:
    """Get current time in specified timezone."""
    tz = get_timezone(tz_name)
    return datetime.now(tz)


def days_ago(days: int, tz_name: str = "Europe/Athens") -> datetime:
    """Get datetime N days ago in specified timezone."""
    tz = get_timezone(tz_name)
    return now_in_tz(tz_name) - timedelta(days=days)


def parse_date(date_string: str, tz_name: str = "Europe/Athens") -> Optional[datetime]:
    """Parse date string and localize to timezone."""
    try:
        dt = date_parser.parse(date_string)
        if dt.tzinfo is None:
            tz = get_timezone(tz_name)
            dt = tz.localize(dt)
        else:
            tz = get_timezone(tz_name)
            dt = dt.astimezone(tz)
        return dt
    except (ValueError, TypeError):
        return None


def is_within_timeframe(
    date_obj: datetime,
    since: datetime,
    tz_name: str = "Europe/Athens"
) -> bool:
    """Check if date is within timeframe."""
    if date_obj.tzinfo is None:
        tz = get_timezone(tz_name)
        date_obj = tz.localize(date_obj)
    return date_obj >= since


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """Format datetime object."""
    return dt.strftime(fmt)


def get_iso_timestamp(tz_name: str = "Europe/Athens") -> str:
    """Get current ISO formatted timestamp."""
    return now_in_tz(tz_name).isoformat()


def get_period_label(days: int) -> str:
    """
    Get human-readable period label based on number of days.

    Args:
        days: Number of days in the period

    Returns:
        Period label (e.g., "Daily", "Weekly", "Biweekly", "Monthly", "14-Day")

    Examples:
        >>> get_period_label(1)
        'Daily'
        >>> get_period_label(7)
        'Weekly'
        >>> get_period_label(14)
        'Biweekly'
        >>> get_period_label(10)
        '10-Day'
    """
    if days == 1:
        return "Daily"
    elif days == 7:
        return "Weekly"
    elif days == 14:
        return "Biweekly"
    elif days == 21:
        return "Triweekly"
    elif days == 28 or days == 30 or days == 31:
        return "Monthly"
    else:
        return f"{days}-Day"


# Deduplication utilities
def compute_hash(item: Dict[str, Any]) -> str:
    """Compute hash for an item based on URL and title."""
    url = item.get("url", "")
    title = item.get("title", "")
    content = f"{url}|{title}".lower().strip()
    return hashlib.sha256(content.encode()).hexdigest()


def dedupe_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate items based on URL and title.
    Returns unique items, preserving first occurrence.
    """
    seen_hashes: Set[str] = set()
    unique_items: List[Dict[str, Any]] = []

    for item in items:
        item_hash = compute_hash(item)
        if item_hash not in seen_hashes:
            seen_hashes.add(item_hash)
            unique_items.append(item)

    return unique_items


def dedupe_by_url(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate items based on URL only."""
    seen_urls: Set[str] = set()
    unique_items: List[Dict[str, Any]] = []

    for item in items:
        url = item.get("url", "").strip().lower()
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_items.append(item)
        elif not url:
            # Keep items without URLs
            unique_items.append(item)

    return unique_items


def merge_duplicates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge duplicate items, combining their data.
    Items with same URL get merged, keeping the most complete data.
    """
    url_map: Dict[str, Dict[str, Any]] = {}

    for item in items:
        url = item.get("url", "").strip()
        if not url:
            continue

        if url not in url_map:
            url_map[url] = item.copy()
        else:
            # Merge: prefer non-empty values
            existing = url_map[url]
            for key, value in item.items():
                if value and (not existing.get(key) or len(str(value)) > len(str(existing.get(key, "")))):
                    existing[key] = value

    return list(url_map.values())


# HTML normalization utilities
def strip_html_tags(html: str) -> str:
    """Remove all HTML tags and return plain text."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(separator=" ", strip=True)


def extract_main_content(html: str) -> str:
    """Extract main content from HTML using readability."""
    try:
        doc = Document(html)
        content_html = doc.summary()
        return strip_html_tags(content_html)
    except Exception:
        return strip_html_tags(html)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Replace multiple newlines with single newline
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    text = normalize_whitespace(text)
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text.strip()


def extract_links(html: str, base_url: Optional[str] = None) -> list:
    """Extract all links from HTML."""
    soup = BeautifulSoup(html, "lxml")
    links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        text = a_tag.get_text(strip=True)

        # Make absolute URLs if base_url provided
        if base_url and href.startswith("/"):
            href = base_url.rstrip("/") + href

        if href and not href.startswith("#"):
            links.append({"url": href, "text": text})

    return links


def html_to_markdown_simple(html: str) -> str:
    """Convert simple HTML to Markdown."""
    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")

    # Replace common tags
    for tag in soup.find_all("strong"):
        tag.replace_with(f"**{tag.get_text()}**")

    for tag in soup.find_all("em"):
        tag.replace_with(f"*{tag.get_text()}*")

    for tag in soup.find_all("code"):
        tag.replace_with(f"`{tag.get_text()}`")

    for tag in soup.find_all("a", href=True):
        text = tag.get_text()
        href = tag["href"]
        tag.replace_with(f"[{text}]({href})")

    return clean_text(soup.get_text())


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix


def is_drupal_url(url: str) -> bool:
    """Check if URL is from drupal.org domain."""
    return "drupal.org" in url.lower()


# Safe I/O utilities
def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if needed."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_write_json(data: Any, filepath: Path, indent: int = 2) -> bool:
    """Safely write JSON to file."""
    try:
        filepath = Path(filepath)
        ensure_dir(filepath.parent)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing JSON to {filepath}: {e}")
        return False


def safe_read_json(filepath: Path) -> Optional[Dict[str, Any]]:
    """Safely read JSON from file."""
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON from {filepath}: {e}")
        return None


def safe_write_text(text: str, filepath: Path, encoding: str = 'utf-8') -> bool:
    """Safely write text to file."""
    try:
        filepath = Path(filepath)
        ensure_dir(filepath.parent)

        with open(filepath, 'w', encoding=encoding) as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Error writing text to {filepath}: {e}")
        return False


def safe_read_text(filepath: Path, encoding: str = 'utf-8') -> Optional[str]:
    """Safely read text from file."""
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Error reading text from {filepath}: {e}")
        return None


def safe_read_yaml(filepath: Path) -> Optional[Dict[str, Any]]:
    """Safely read YAML from file."""
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading YAML from {filepath}: {e}")
        return None


def file_exists(filepath: Path) -> bool:
    """Check if file exists."""
    return Path(filepath).exists()


def get_file_size(filepath: Path) -> int:
    """Get file size in bytes."""
    try:
        return Path(filepath).stat().st_size
    except Exception:
        return 0


def list_files(directory: Path, pattern: str = "*") -> list:
    """List files in directory matching pattern."""
    try:
        directory = Path(directory)
        if not directory.exists():
            return []
        return list(directory.glob(pattern))
    except Exception:
        return []