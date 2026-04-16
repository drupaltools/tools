"""Unified content reader for Drupal Aggregator.

This module combines RSS feed reading and web page scraping into a single interface.
"""

import feedparser
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from drupal_news.utils.consolidated_utils import parse_date, is_within_timeframe, strip_html_tags, clean_text, truncate_text, extract_links
from drupal_news.cache_manager import CacheManager


def normalize_page_config(page_source: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalize page source to standard config format.

    Args:
        page_source: Either a URL string or a config dict with url and selectors

    Returns:
        Dict with 'url' and optional 'selectors'
    """
    if isinstance(page_source, str):
        return {"url": page_source, "selectors": None}
    elif isinstance(page_source, dict):
        return {
            "url": page_source.get("url"),
            "selectors": page_source.get("selectors"),
            "name": page_source.get("name", ""),
            "base_url": page_source.get("base_url", "")
        }
    else:
        raise ValueError(f"Invalid page source format: {type(page_source)}")


def fetch_content(
    rss_urls: List[str],
    page_sources: List[Union[str, Dict[str, Any]]],
    since: datetime,
    timezone: str,
    cache: Optional[CacheManager] = None,
    timeout: int = 20,
    retries: int = 2,
    user_agent: str = "DrupalNewsBot/1.0"
) -> List[Dict[str, Any]]:
    """
    Fetch content from both RSS feeds and web pages.

    Args:
        rss_urls: List of RSS feed URLs
        page_sources: List of page URLs or config objects to scrape
        since: Datetime threshold for filtering items
        timezone: Timezone name
        cache: Optional cache manager
        timeout: HTTP timeout in seconds
        retries: Number of retry attempts
        user_agent: User agent string

    Returns:
        List of normalized items from both RSS and web pages
    """
    items = []

    # Fetch RSS feeds
    rss_items = fetch_rss_feeds(rss_urls, since, timezone, cache, timeout, retries, user_agent)
    items.extend(rss_items)

    # Fetch web pages
    page_items = fetch_web_pages(page_sources, since, timezone, cache, timeout, retries, user_agent)
    items.extend(page_items)

    return items


def fetch_rss_feeds(
    rss_urls: List[str],
    since: datetime,
    timezone: str,
    cache: Optional[CacheManager] = None,
    timeout: int = 20,
    retries: int = 2,
    user_agent: str = "DrupalNewsBot/1.0"
) -> List[Dict[str, Any]]:
    """
    Fetch and normalize RSS feeds.

    Args:
        rss_urls: List of RSS feed URLs
        since: Datetime threshold for filtering items
        timezone: Timezone name
        cache: Optional cache manager
        timeout: HTTP timeout in seconds
        retries: Number of retry attempts
        user_agent: User agent string

    Returns:
        List of normalized items
    """
    items = []

    for url in rss_urls:
        try:
            # Check cache first
            if cache:
                cached = cache.get(url)
                if cached:
                    items.extend(cached.get("items", []))
                    continue

            # Fetch RSS feed
            headers = {"User-Agent": user_agent}
            response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
            response.raise_for_status()

            # Parse feed
            feed = feedparser.parse(response.content)

            feed_items = []
            for entry in feed.entries:
                # Extract data
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                description = entry.get("description") or entry.get("summary", "")
                pub_date = entry.get("published") or entry.get("updated", "")

                if not title or not link:
                    continue

                # Parse and check date
                date_obj = parse_date(pub_date, timezone)
                if date_obj and not is_within_timeframe(date_obj, since, timezone):
                    continue

                # Clean description
                description = strip_html_tags(description)
                description = clean_text(description)
                description = truncate_text(description, 500)

                item = {
                    "title": title,
                    "url": link,
                    "description": description,
                    "date": date_obj.isoformat() if date_obj else pub_date,
                    "source_type": "rss",
                    "source_url": url,
                    "tags": [tag.get("term", "") for tag in entry.get("tags", [])]
                }

                feed_items.append(item)

            # Cache the results
            if cache and feed_items:
                cache.set(url, {"items": feed_items})

            items.extend(feed_items)

        except httpx.HTTPError as e:
            print(f"HTTP error fetching RSS {url}: {e}")
        except Exception as e:
            print(f"Error processing RSS {url}: {e}")

    return items


def fetch_web_pages(
    page_sources: List[Union[str, Dict[str, Any]]],
    since: datetime,
    timezone: str,
    cache: Optional[CacheManager] = None,
    timeout: int = 20,
    retries: int = 2,
    user_agent: str = "DrupalNewsBot/1.0"
) -> List[Dict[str, Any]]:
    """
    Fetch and scrape web pages for news items.

    Args:
        page_sources: List of page URLs or config objects to scrape
        since: Datetime threshold for filtering items
        timezone: Timezone name
        cache: Optional cache manager
        timeout: HTTP timeout in seconds
        retries: Number of retry attempts
        user_agent: User agent string

    Returns:
        List of normalized items
    """
    items = []

    for page_source in page_sources:
        try:
            # Normalize config
            config = normalize_page_config(page_source)
            url = config["url"]
            selectors = config.get("selectors")
            base_url = config.get("base_url") or "https://www.drupal.org"

            # Check cache first
            if cache:
                cached = cache.get(url)
                if cached:
                    items.extend(cached.get("items", []))
                    continue

            # Fetch page
            headers = {"User-Agent": user_agent}
            response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
            response.raise_for_status()

            # Parse based on selectors or URL pattern
            if selectors:
                # Use custom selectors
                page_items = _parse_with_selectors(response.text, url, since, timezone, selectors, base_url)
            elif "drupal.org/news" in url:
                page_items = _parse_drupal_news(response.text, url, since, timezone)
            elif "drupal.org/planet" in url:
                page_items = _parse_drupal_planet(response.text, url, since, timezone)
            elif "drupal.org/project/drupal/releases" in url:
                page_items = _parse_drupal_releases(response.text, url, since, timezone)
            else:
                page_items = _parse_generic_page(response.text, url, since, timezone)

            # Cache the results
            if cache and page_items:
                cache.set(url, {"items": page_items})

            items.extend(page_items)

        except httpx.HTTPError as e:
            print(f"HTTP error fetching page {url}: {e}")
        except Exception as e:
            print(f"Error processing page {url}: {e}")

    return items


def _parse_with_selectors(
    html: str,
    source_url: str,
    since: datetime,
    timezone: str,
    selectors: Dict[str, str],
    base_url: str = "https://www.drupal.org"
) -> List[Dict[str, Any]]:
    """
    Parse HTML using custom CSS selectors.

    Args:
        html: HTML content
        source_url: Source URL
        since: Datetime threshold
        timezone: Timezone name
        selectors: Dict of CSS selectors for different elements
        base_url: Base URL for making relative URLs absolute

    Selector keys:
        - container: Container element for items (required)
        - title: Title element (required)
        - link: Link element (defaults to title if not provided)
        - description: Description element (optional)
        - date: Date element (optional)

    Returns:
        List of normalized items
    """
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Get container selector
    container_selector = selectors.get("container")
    if not container_selector:
        print(f"Warning: No container selector provided for {source_url}")
        return items

    # Find all containers
    containers = soup.select(container_selector)

    for container in containers[:20]:  # Limit to 20 items
        try:
            # Extract title
            title_selector = selectors.get("title")
            if not title_selector:
                continue

            title_elem = container.select_one(title_selector)
            if not title_elem:
                continue

            title = clean_text(title_elem.get_text())
            if not title:
                continue

            # Extract link
            link_selector = selectors.get("link", title_selector)
            link_elem = container.select_one(link_selector)

            if link_elem and link_elem.name == "a":
                link = link_elem.get("href", "")
            elif link_elem:
                # If link selector doesn't point to <a>, find <a> inside it
                link_tag = link_elem.find("a")
                link = link_tag.get("href", "") if link_tag else ""
            else:
                link = source_url

            # Make absolute URL
            if link.startswith("/"):
                link = base_url + link
            elif not link.startswith("http"):
                link = source_url

            # Extract description
            description = ""
            desc_selector = selectors.get("description")
            if desc_selector:
                desc_elem = container.select_one(desc_selector)
                if desc_elem:
                    description = truncate_text(clean_text(desc_elem.get_text()), 500)

            # Extract date
            date_obj = None
            date_selector = selectors.get("date")
            if date_selector:
                date_elem = container.select_one(date_selector)
                if date_elem:
                    date_str = date_elem.get("datetime", "") or date_elem.get_text()
                    date_obj = parse_date(date_str, timezone) if date_str else None

                    # Filter by date if provided
                    if date_obj and not is_within_timeframe(date_obj, since, timezone):
                        continue

            items.append({
                "title": title,
                "url": link,
                "description": description,
                "date": date_obj.isoformat() if date_obj else "",
                "source_type": "page",
                "source_url": source_url,
                "tags": []
            })

        except Exception as e:
            print(f"Error parsing item from {source_url}: {e}")
            continue

    return items


def _parse_drupal_news(html: str, source_url: str, since: datetime, timezone: str) -> List[Dict[str, Any]]:
    """Parse drupal.org/news page."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Find news articles
    articles = soup.find_all("article") or soup.find_all("div", class_=["node", "view-content"])

    for article in articles[:20]:  # Limit to recent items
        # Extract title and link
        title_tag = article.find("h2") or article.find("h3")
        if not title_tag:
            continue

        link_tag = title_tag.find("a") or article.find("a")
        if not link_tag or not link_tag.get("href"):
            continue

        title = clean_text(title_tag.get_text())
        link = link_tag["href"]

        # Make absolute URL
        if link.startswith("/"):
            link = "https://www.drupal.org" + link

        # Extract description
        description = ""
        desc_tag = article.find("div", class_="field--name-body") or article.find("p")
        if desc_tag:
            description = truncate_text(clean_text(desc_tag.get_text()), 500)

        # Extract date
        date_tag = article.find("time") or article.find("span", class_="date")
        date_str = date_tag.get("datetime", "") or date_tag.get_text() if date_tag else ""

        date_obj = parse_date(date_str, timezone) if date_str else None
        if date_obj and not is_within_timeframe(date_obj, since, timezone):
            continue

        items.append({
            "title": title,
            "url": link,
            "description": description,
            "date": date_obj.isoformat() if date_obj else "",
            "source_type": "page",
            "source_url": source_url,
            "tags": ["news"]
        })

    return items


def _parse_drupal_planet(html: str, source_url: str, since: datetime, timezone: str) -> List[Dict[str, Any]]:
    """Parse drupal.org/planet page."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Find planet entries
    entries = soup.find_all("article") or soup.find_all("div", class_="view-content")

    for entry in entries[:20]:
        title_tag = entry.find("h2") or entry.find("h3")
        if not title_tag:
            continue

        link_tag = title_tag.find("a")
        if not link_tag or not link_tag.get("href"):
            continue

        title = clean_text(title_tag.get_text())
        link = link_tag["href"]

        # Make absolute URL if needed
        if link.startswith("/"):
            link = "https://www.drupal.org" + link

        # Extract description
        description = ""
        desc_tag = entry.find("div", class_="content") or entry.find("p")
        if desc_tag:
            description = truncate_text(clean_text(desc_tag.get_text()), 500)

        # Extract date
        date_tag = entry.find("time") or entry.find("span", class_="date")
        date_str = date_tag.get("datetime", "") or date_tag.get_text() if date_tag else ""

        date_obj = parse_date(date_str, timezone) if date_str else None
        if date_obj and not is_within_timeframe(date_obj, since, timezone):
            continue

        items.append({
            "title": title,
            "url": link,
            "description": description,
            "date": date_obj.isoformat() if date_obj else "",
            "source_type": "page",
            "source_url": source_url,
            "tags": ["planet"]
        })

    return items


def _parse_drupal_releases(html: str, source_url: str, since: datetime, timezone: str) -> List[Dict[str, Any]]:
    """Parse drupal.org/project/drupal/releases page."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Find release entries
    releases = soup.find_all("div", class_=["view-project-release-by-project", "views-row"])

    for release in releases[:15]:
        # Extract version
        version_tag = release.find("h2") or release.find("span", class_="field--name-field-release-version")
        if not version_tag:
            continue

        version = clean_text(version_tag.get_text())
        title = f"Drupal {version}"

        # Extract link
        link_tag = release.find("a", href=True)
        link = link_tag["href"] if link_tag else source_url

        if link.startswith("/"):
            link = "https://www.drupal.org" + link

        # Extract date
        date_tag = release.find("time") or release.find("span", class_="date")
        date_str = date_tag.get("datetime", "") or date_tag.get_text() if date_tag else ""

        date_obj = parse_date(date_str, timezone) if date_str else None
        if date_obj and not is_within_timeframe(date_obj, since, timezone):
            continue

        # Description
        desc_tag = release.find("div", class_="field--name-body")
        description = truncate_text(clean_text(desc_tag.get_text()), 500) if desc_tag else f"Drupal {version} release"

        items.append({
            "title": title,
            "url": link,
            "description": description,
            "date": date_obj.isoformat() if date_obj else "",
            "source_type": "page",
            "source_url": source_url,
            "tags": ["release", "core"]
        })

    return items


def _parse_generic_page(html: str, source_url: str, since: datetime, timezone: str) -> List[Dict[str, Any]]:
    """Generic page parser."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Extract all article or content blocks
    articles = soup.find_all(["article", "div"], class_=lambda x: x and "content" in x.lower())

    for article in articles[:10]:
        title_tag = article.find(["h1", "h2", "h3"])
        if not title_tag:
            continue

        title = clean_text(title_tag.get_text())
        link_tag = article.find("a", href=True)
        link = link_tag["href"] if link_tag else source_url

        if link.startswith("/"):
            link = "https://www.drupal.org" + link

        description_tag = article.find("p")
        description = truncate_text(clean_text(description_tag.get_text()), 500) if description_tag else ""

        items.append({
            "title": title,
            "url": link,
            "description": description,
            "date": "",
            "source_type": "page",
            "source_url": source_url,
            "tags": []
        })

    return items


# Convenience functions for backward compatibility
def fetch_rss(*args, **kwargs):
    """Backward compatibility function - deprecated, use fetch_rss_feeds instead."""
    return fetch_rss_feeds(*args, **kwargs)


def fetch_pages(*args, **kwargs):
    """Backward compatibility function - deprecated, use fetch_web_pages instead."""
    return fetch_web_pages(*args, **kwargs)