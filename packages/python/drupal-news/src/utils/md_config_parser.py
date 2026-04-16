#!/usr/bin/env python3
"""
Markdown configuration parser for sources.md
Parses RSS feeds and web pages from markdown format
"""

import re
from typing import Dict, List
from pathlib import Path


def parse_sources_md(file_path: str) -> Dict[str, List[str]]:
    """
    Parse sources.md file and extract RSS feeds and web pages.

    Args:
        file_path: Path to sources.md file

    Returns:
        Dictionary with 'rss' and 'pages' keys containing lists of URLs

    Example markdown format:
        ## RSS Feeds
        - https://example.com/feed1
        - https://example.com/feed2

        ## Web Pages
        - https://example.com/page1
        - https://example.com/page2
    """
    sources = {
        "rss": [],
        "pages": []
    }

    path = Path(file_path)
    if not path.exists():
        return sources

    content = path.read_text(encoding='utf-8')

    # Split into sections based on ## headers
    current_section = None

    for line in content.split('\n'):
        line = line.strip()

        # Check for section headers
        if line.startswith('## '):
            header = line[3:].strip().lower()
            if 'rss' in header:
                current_section = 'rss'
            elif 'page' in header or 'web' in header:
                current_section = 'pages'
            else:
                current_section = None
            continue

        # Parse URLs from list items
        if current_section and line.startswith('- '):
            url = line[2:].strip()
            # Basic URL validation
            if url.startswith('http://') or url.startswith('https://'):
                sources[current_section].append(url)

    return sources


def merge_sources_config(json_config: dict, md_file: str = None) -> dict:
    """
    Merge sources from markdown file with JSON config.
    Markdown sources take precedence if both exist.

    Args:
        json_config: The config dictionary loaded from JSON
        md_file: Path to markdown sources file (default: sources.md in project root)

    Returns:
        Updated config dictionary with sources from markdown if available
    """
    if md_file is None:
        # Default to sources.md in the project root
        md_file = Path(__file__).parent.parent.parent / 'sources.md'

    md_sources = parse_sources_md(str(md_file))

    # If markdown has sources, use them; otherwise keep JSON sources
    if md_sources['rss'] or md_sources['pages']:
        if 'sources' not in json_config:
            json_config['sources'] = {}

        if md_sources['rss']:
            json_config['sources']['rss'] = md_sources['rss']
        if md_sources['pages']:
            json_config['sources']['pages'] = md_sources['pages']

    return json_config


if __name__ == '__main__':
    # Test the parser
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'sources.md'

    sources = parse_sources_md(file_path)
    print(f"RSS Feeds: {len(sources['rss'])}")
    for url in sources['rss']:
        print(f"  - {url}")

    print(f"\nWeb Pages: {len(sources['pages'])}")
    for url in sources['pages']:
        print(f"  - {url}")
