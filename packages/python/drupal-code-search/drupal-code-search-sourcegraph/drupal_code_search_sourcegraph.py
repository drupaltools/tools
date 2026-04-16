#!/usr/bin/env python3
"""Search Drupal core on Sourcegraph.com using src-cli.

Usage:
    ./search-03.py "hook_form_alter"
    ./search-03.py "EntityTypeManager" --version 10
    ./search-03.py "implements TokenInterface" --json
    ./search-03.py "class.*Block" -n 10
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

DRUPAL_REPO = "github\\.com/drupal/drupal"
SOURCEGRAPH_URL = "https://sourcegraph.com"

VERSIONS = {
    "7": "refs/heads/7.x",
    "9": "refs/heads/9.5.x",
    "10": "refs/heads/10.0.x",
    "11": "refs/heads/11.0.x",
    "main": "refs/heads/main",
}


class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"


def find_src_cli():
    for name in ("src-cli", "src"):
        path = shutil.which(name)
        if path:
            return name
    print(f"{Colors.RED}Error: src-cli not found.{Colors.END}")
    print(f"  Install: https://github.com/sourcegraph/src-cli")
    print(f"  Or: brew install sourcegraph/src-cli/src-cli")
    sys.exit(1)


def build_query(term: str, version: str) -> str:
    rev = VERSIONS.get(version, VERSIONS["main"])
    return f"context:global repo:^{DRUPAL_REPO} rev:{rev} {term}"


def load_env() -> None:
    script_path = Path(__file__).resolve().parent.parent
    env_path = script_path / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            if key not in os.environ:
                os.environ[key] = value


def main() -> int:
    load_env()
    parser = argparse.ArgumentParser(
        description="Search Drupal core on Sourcegraph.com via src-cli",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "hook_form_alter"
  %(prog)s "EntityTypeManager" --version 10
  %(prog)s "implements TokenInterface" --json
  %(prog)s "class.*Block" -n 10
  %(prog)s "Drupal\\DrupalCore" --version main --stream
        """,
    )
    parser.add_argument("term", help="Search term or pattern")
    parser.add_argument(
        "--version",
        "-v",
        default="main",
        choices=list(VERSIONS.keys()),
        help="Drupal version branch (default: main)",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=0,
        help="Limit displayed results (streaming mode, default: all)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON from src-cli",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream results as they arrive",
    )
    parser.add_argument(
        "--explain-json",
        action="store_true",
        help="Explain the JSON schema and exit",
    )
    parser.add_argument(
        "--endpoint",
        "-e",
        default=SOURCEGRAPH_URL,
        help=f"Sourcegraph endpoint (default: {SOURCEGRAPH_URL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the src-cli command without running",
    )

    args = parser.parse_args()

    src_cli = find_src_cli()
    query = build_query(args.term, args.version)

    env = os.environ.copy()
    env["SRC_ENDPOINT"] = args.endpoint

    cmd = [src_cli, "search"]
    if args.json:
        cmd.append("-json")
    if args.stream:
        cmd.append("-stream")
    if args.limit > 0:
        cmd.extend(["-display", str(args.limit)])
    if args.explain_json:
        cmd.append("-explain-json")
    cmd.append(query)

    print(
        f"{Colors.BOLD}Searching Drupal {args.version}{Colors.END} "
        f"({VERSIONS[args.version]})"
    )
    print(f"{Colors.CYAN}{args.endpoint}{Colors.END}")
    print(f"{Colors.BLUE}Query: {query}{Colors.END}\n")

    if args.dry_run:
        print("Would run:", " ".join(cmd))
        print(f"Endpoint: {env['SRC_ENDPOINT']}")
        print(
            f"SRC_ACCESS_TOKEN: {'(set)' if env.get('SRC_ACCESS_TOKEN') else '(unset)'}"
        )

        if src_cli not in shutil.which(src_cli):
            print(f"{Colors.YELLOW}Warning: {src_cli} not in PATH{Colors.END}")
        return 0

    try:
        result = subprocess.run(
            cmd,
            env=env,
            check=False,
        )
        return result.returncode
    except FileNotFoundError:
        print(f"{Colors.RED}Error: {src_cli} not found in PATH{Colors.END}")
        print(f"  Install: https://github.com/sourcegraph/src-cli")
        return 1


if __name__ == "__main__":
    sys.exit(main())
