"""Validator for Drupal Aggregator data."""
from typing import List, Dict, Any
from urllib.parse import urlparse
import re


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_item(item: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate a single news item.

    Args:
        item: Item dictionary to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Required fields
    if not item.get("title"):
        errors.append("Missing title")

    if not item.get("url"):
        errors.append("Missing URL")
    elif not validate_url(item["url"]):
        errors.append(f"Invalid URL: {item.get('url')}")

    if not item.get("source_type"):
        errors.append("Missing source_type")
    elif item["source_type"] not in ["rss", "page"]:
        errors.append(f"Invalid source_type: {item.get('source_type')}")

    return (len(errors) == 0, errors)


def validate_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate all items and generate report.

    Args:
        items: List of items to validate

    Returns:
        Validation report dictionary
    """
    rss_count = sum(1 for item in items if item.get("source_type") == "rss")
    page_count = sum(1 for item in items if item.get("source_type") == "page")
    missing_links = 0
    invalid_urls = 0
    all_errors = []

    for item in items:
        is_valid, errors = validate_item(item)

        if not is_valid:
            all_errors.extend(errors)

            if "Missing URL" in str(errors):
                missing_links += 1

            if any("Invalid URL" in e for e in errors):
                invalid_urls += 1

    report = {
        "rss_count": rss_count,
        "page_count": page_count,
        "total_count": len(items),
        "missing_links": missing_links,
        "invalid_urls": invalid_urls,
        "passed": len(all_errors) == 0,
        "errors": all_errors[:50]  # Limit error list
    }

    return report


def validate_markdown_links(markdown_text: str) -> Dict[str, Any]:
    """
    Validate that markdown contains proper source links.

    Args:
        markdown_text: Markdown text to check

    Returns:
        Dictionary with validation results
    """
    # Find all markdown links
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(link_pattern, markdown_text)

    # Find drupal.org links
    drupal_links = [url for _, url in matches if "drupal.org" in url]

    # Find "source" links
    source_links = [url for text, url in matches if "source" in text.lower()]

    return {
        "total_links": len(matches),
        "drupal_links": len(drupal_links),
        "source_links": len(source_links),
        "has_references": len(source_links) > 0 or len(drupal_links) > 0
    }


def validate_summary(summary_text: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate AI-generated summary.

    Args:
        summary_text: Summary markdown text
        items: Original items that were summarized

    Returns:
        Validation results
    """
    link_validation = validate_markdown_links(summary_text)

    # Check for "No significant" message
    has_no_updates = "no significant" in summary_text.lower()

    # Word count
    word_count = len(summary_text.split())

    # Check for key sections
    has_structure = any(header in summary_text for header in ["##", "###", "**"])

    return {
        "word_count": word_count,
        "has_references": link_validation["has_references"],
        "total_links": link_validation["total_links"],
        "drupal_links": link_validation["drupal_links"],
        "has_structure": has_structure,
        "has_no_updates_message": has_no_updates,
        "items_count": len(items),
        "passed": link_validation["has_references"] and word_count > 100
    }
