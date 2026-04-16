"""CLI entry point for drupal_web_search."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from drupal_web_search.config import load_config
from drupal_web_search.search import results_to_dicts, search_web


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search the web using DDGS with configurable engine fallback.",
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--engine", help="Preferred search engine override")
    parser.add_argument("--json", action="store_true", help="Print results as JSON")
    parser.add_argument("--limit", type=int, help="Maximum number of results to return")
    parser.add_argument("--verbose", action="store_true", help="Print config and engine details")
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional path to a config.toml file",
    )
    parser.add_argument(
        "--site",
        action="append",
        default=[],
        help="Restrict results to a domain (e.g. drupal.org). Pass multiple times for multiple domains.",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Print loaded config and exit",
    )
    return parser


def print_text_results(results: list[dict[str, str]]) -> None:
    for index, result in enumerate(results, start=1):
        print(f"{index}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Snippet: {result['snippet'] or '(no snippet)'}")
        print(f"   Engine: {result['engine']}")
        print()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit must be greater than zero.")

    try:
        config = load_config(args.config)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.show_config:
        print(f"Config file: {config.config_path}")
        print(f"Default engine: {config.default_engine}")
        print(f"Fallback order: {config.fallback_order}")
        print(f"Search num_results: {config.search.num_results}")
        print(f"Search safe_search: {config.search.safe_search}")
        print(f"Search timeout: {config.search.timeout}")
        print(f"Site preferences restrict_to: {config.site_preferences.restrict_to}")
        print(f"Site preferences preferred: {config.site_preferences.preferred}")
        print(f"Site preferences blocked: {config.site_preferences.blocked}")
        print("Engines:")
        for name, eng in config.engines.items():
            print(f"  {name}: enabled={eng.enabled}")
        return 0

    if args.verbose:
        print(f"[verbose] Config: {config.config_path}", file=sys.stderr)
        if args.engine:
            print(
                f"[verbose] Engine: {args.engine} (--engine overrides default and fallback)",
                file=sys.stderr,
            )
        else:
            print(
                f"[verbose] Engine: {config.default_engine} (fallback: {', '.join(config.fallback_order) or 'none'})",
                file=sys.stderr,
            )
        print(f"[verbose] Query: {args.query}", file=sys.stderr)
        if args.site:
            print(f"[verbose] Site restrict: {args.site}", file=sys.stderr)

    try:
        results = search_web(
            query=args.query,
            config=config,
            requested_engine=args.engine,
            limit=args.limit,
            site=args.site,
        )
    except Exception as exc:
        if args.verbose:
            print(f"[verbose] Error: {exc}", file=sys.stderr)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1

    serialized_results = results_to_dicts(results)
    if args.json:
        print(json.dumps(serialized_results, indent=2))
        return 0

    if not serialized_results:
        print("No results found.")
        return 0

    print_text_results(serialized_results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
