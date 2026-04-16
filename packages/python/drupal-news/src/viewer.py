#!/usr/bin/env python3
"""
Web viewer for Drupal News Aggregator results.
Renders parsed.md and summary.md in a browser interface.
"""
import os
import sys
import re
import subprocess
import argparse
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
import markdown


def get_current_version() -> str:
    """
    Get the current version from git tag.

    Returns:
        String with the current git tag version, or "unknown" if not available
    """
    try:
        # Try to get the current git tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            if version.startswith('v'):
                return version[1:]  # Remove 'v' prefix if present
            return version
        else:
            # Fallback to checking the latest tag
            result = subprocess.run(
                ["git", "tag", "--sort=-version:refname"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            if result.returncode == 0:
                tags = result.stdout.strip().split('\n')
                if tags and tags[0]:
                    version = tags[0]
                    if version.startswith('v'):
                        return version[1:]  # Remove 'v' prefix if present
                    return version
    except Exception:
        pass

    return "unknown"


def get_static_folder():
    """Determine the static folder location."""
    # Check if static folder exists in current working directory
    cwd_static = Path.cwd() / "static"
    if cwd_static.exists():
        return str(cwd_static)

    # Try to find static folder relative to the package using importlib.resources
    try:
        import importlib.resources as pkg_resources
        import drupal_news
        from drupal_news import static  # Import the static module/package

        # Use importlib.resources to get the static directory
        static_path = pkg_resources.files(drupal_news) / "static"
        if static_path.is_dir():
            return str(static_path)
    except (ImportError, AttributeError):
        pass

    # Try to find static folder relative to the package (fallback)
    try:
        import drupal_news
        package_root = Path(drupal_news.__file__).parent.parent
        package_static = package_root / "static"
        if package_static.exists():
            return str(package_static)
    except (ImportError, AttributeError):
        pass

    # Fall back to package static folder (for development)
    package_static = Path(__file__).parent.parent / "static"
    if package_static.exists():
        return str(package_static)

    # Last resort: current directory
    return 'static'


app = Flask(__name__, static_folder=get_static_folder(), static_url_path='/static')


def get_run_root():
    """
    Determine the runs directory location.
    Priority: ENV var > config.yml > current working directory.
    """
    # 1. Check environment variable
    env_run_root = os.getenv("DRUPAL_NEWS_RUN_ROOT")
    if env_run_root:
        return Path(env_run_root)

    # 2. Try loading from config.yml
    config_path = Path.cwd() / "config.yml"
    if config_path.exists():
        try:
            from drupal_news.utils.config_loader import load_config
            config = load_config(str(config_path))
            if "run_root" in config:
                return Path(config["run_root"])
        except Exception:
            pass  # Fall through to default

    # 3. Default to current working directory + runs
    return Path.cwd() / "runs"


# Configuration
RUN_ROOT = get_run_root()


def get_available_runs():
    """Get list of available run directories."""
    if not RUN_ROOT.exists():
        return []
    runs = [d.name for d in RUN_ROOT.iterdir() if d.is_dir()]
    return sorted(runs, reverse=True)


def read_markdown_file(run_date, filename):
    """Read markdown file and convert to HTML."""
    file_path = RUN_ROOT / run_date / filename
    if not file_path.exists():
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    # Convert plain URLs in table cells to links
    def linkify_url(match):
        url = match.group(1)
        return f'<td><a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></td>'

    html_content = re.sub(
        r'<td>(https?://[^<]+)</td>',
        linkify_url,
        html_content
    )

    # Add target="_blank" to all existing links
    html_content = re.sub(
        r'<a\s+([^>]*?)href=',
        r'<a \1target="_blank" rel="noopener noreferrer" href=',
        html_content
    )

    return html_content


def read_json_file(run_date, filename):
    """Read JSON file."""
    file_path = RUN_ROOT / run_date / filename
    if not file_path.exists():
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drupal News Viewer - {{ run_date }}</title>
    <link crossorigin="anonymous" media="all" rel="stylesheet" href="/static/css/viewer.css" />
</head>
<body>
    <header>
        <h1>💧 Drupal News Viewer</h1>
    </header>

    <div class="container">
        <div class="controls">
            <div>
                <label for="run-select">Select date: </label>
                <select id="run-select" onchange="changeRun(this.value)">
                    {% for run in runs %}
                    <option value="{{ run }}" {% if run == run_date %}selected{% endif %}>{{ run }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>

        <div id="tabs-view" class="active">
            <div class="tabs">
                <button class="tab active" onclick="showTab('summary')">Summary</button>
                <button class="tab" onclick="showTab('parsed')">Parsed Data</button>
                <button class="tab" onclick="showTab('metrics')">Metrics</button>
                <button class="tab" onclick="showTab('log')">Log</button>
            </div>

            <div class="content markdown-content">
                <div id="summary-content" class="tab-content active">
                    {% if summary %}
                        {{ summary|safe }}
                    {% else %}
                        <div class="no-data">Summary not available</div>
                    {% endif %}
                </div>

                <div id="parsed-content" class="tab-content">
                    {% if parsed %}
                        {{ parsed|safe }}
                    {% else %}
                        <div class="no-data">Parsed data not available</div>
                    {% endif %}
                </div>

                <div id="metrics-content" class="tab-content">
                    {% if metrics %}
                        <h2>Run Metrics</h2>
                        <pre>{{ metrics }}</pre>
                    {% else %}
                        <div class="no-data">Metrics not available</div>
                    {% endif %}
                </div>

                <div id="log-content" class="tab-content">
                    {% if log %}
                        <h2>Run Log</h2>
                        <pre>{{ log }}</pre>
                    {% else %}
                        <div class="no-data">Log not available</div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + '-content').classList.add('active');

            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        function changeRun(runDate) {
            window.location.href = '/run/' + runDate;
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Show latest run."""
    runs = get_available_runs()
    if not runs:
        return "<h1>No runs available</h1><p>Run the aggregator first to generate data.</p>"

    return view_run(runs[0])


@app.route('/run/<run_date>')
def view_run(run_date):
    """View specific run."""
    runs = get_available_runs()
    if run_date not in runs:
        return f"<h1>Run not found: {run_date}</h1>", 404

    summary_html = read_markdown_file(run_date, 'summary.md')
    parsed_html = read_markdown_file(run_date, 'parsed.md')
    metrics_json = read_json_file(run_date, 'metrics.json')
    log_text = read_json_file(run_date, 'run.log')

    return render_template_string(
        HTML_TEMPLATE,
        run_date=run_date,
        runs=runs,
        summary=summary_html,
        parsed=parsed_html,
        metrics=metrics_json,
        log=log_text
    )


@app.route('/api/runs')
def api_runs():
    """API endpoint to list all runs."""
    runs = get_available_runs()
    return jsonify(runs)


if __name__ == '__main__':
    # Check for --version flag first
    if '--version' in sys.argv:
        print(f"drupal-news-viewer version {get_current_version()}")
        sys.exit(0)

    # Parse arguments
    parser = argparse.ArgumentParser(description="Drupal News Viewer")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on (default: 5000)")
    args = parser.parse_args()

    print("=" * 60)
    print("Drupal News Viewer")
    print("=" * 60)
    print(f"Run root: {RUN_ROOT}")
    print(f"Available runs: {len(get_available_runs())}")
    print(f"\nStarting server on http://localhost:{args.port}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=args.port)
