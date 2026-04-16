#!/usr/bin/env python3
"""Get the latest stable and supported Drupal versions from the CLI."""

import re
import sys
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser


class DrupalReleasesParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.versions: list[str] = []
        self.dates: list[str] = []
        self._in_version = False
        self._in_date = False
        self._version_buf: str = ""
        self._date_buf: str = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = dict(attrs).get("class", "")
        if "views-field-field-release-version" in classes:
            if "h4" in classes:
                self._in_version = True
                self._version_buf = ""
            if "release-date" in classes:
                self._in_date = True
                self._date_buf = ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "h4" and self._in_version:
            version = self._version_buf.strip()
            if "dev" not in version.lower():
                version = re.sub(
                    r"^Drupal core\s*", "", version, flags=re.IGNORECASE
                ).strip()
                self.versions.append(version)
            self._in_version = False
        if tag == "span" and self._in_date:
            date_str = self._date_buf.strip()
            date_str = re.sub(
                r"^Released\s*", "", date_str, flags=re.IGNORECASE
            ).strip()
            try:
                parsed = datetime.strptime(date_str, "%B %d, %Y").replace(
                    tzinfo=timezone.utc
                )
                self.dates.append(parsed.strftime("%Y-%m-%d"))
            except ValueError:
                self.dates.append(date_str)
            self._in_date = False

    def handle_data(self, data: str) -> None:
        if self._in_version:
            self._version_buf += data
        if self._in_date:
            self._date_buf += data


def fetch_releases(
    url: str = "https://www.drupal.org/project/drupal",
) -> list[tuple[str, str]]:
    with urllib.request.urlopen(url, timeout=30) as response:
        body = response.read().decode("utf-8")

    parser = DrupalReleasesParser()
    parser.feed(body)

    return list(zip(parser.dates, parser.versions))


def main() -> int:
    try:
        releases = fetch_releases()
    except Exception as exc:
        print(f"Error fetching releases: {exc}", file=sys.stderr)
        return 1

    if not releases:
        print(
            "No releases found — CSS selectors may have changed on drupal.org",
            file=sys.stderr,
        )
        return 1

    for date, version in releases:
        print(f"{date}  {version}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
