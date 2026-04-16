#!/usr/bin/env python3
"""
Drupal News Aggregator - Main Orchestrator

Automated Drupal News aggregator that collects, normalizes, caches, validates,
and summarizes Drupal news via selectable LLMs.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os
import json

# Import modules
from drupal_news.cache_manager import CacheManager
from drupal_news.process_logger import get_logger
from drupal_news.content_reader import fetch_content
from drupal_news.validator import validate_items, validate_summary
from drupal_news.output_formatter import write_parsed_md, write_summary_md, generate_summary_pdf
from drupal_news.ai_summarizer import summarize, summarize_with_fallback, generate_placeholder_summary
from drupal_news.email_sender import send_report, write_email_log
from drupal_news.metrics_collector import collect_metrics
from drupal_news.pipeline_integrity import verify_run_simple
from drupal_news.data_cleaner import run_cleanup
from drupal_news.utils.consolidated_utils import days_ago, get_iso_timestamp, now_in_tz, get_period_label, dedupe_items, safe_write_json, safe_read_json, safe_read_yaml, ensure_dir
from drupal_news.utils.md_config_parser import merge_sources_config
from drupal_news.utils.config_loader import get_config, load_config as load_unified_config, load_providers_config as load_unified_providers


# Exit codes
EXIT_SUCCESS = 0
EXIT_PARTIAL_FETCH = 10
EXIT_VALIDATION_FAILED = 20
EXIT_SUMMARIZER_FAILED = 30
EXIT_EMAIL_FAILED = 40
EXIT_INTEGRITY_FAILED = 50


def load_config(config_path: str = "config.yml") -> dict:
    """
    Load unified configuration from config.yml.

    Args:
        config_path: Path to config.yml file (default: config.yml)

    Returns:
        Configuration dictionary with core and sources sections

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    try:
        config = load_unified_config(str(config_path))
        return config
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}")
        print(f"Create one from the example: cp config.example.yml config.yml")
        sys.exit(1)


def expand_env_vars(data):
    """Recursively expand environment variables in config data."""
    import re
    if isinstance(data, dict):
        return {k: expand_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [expand_env_vars(item) for item in data]
    elif isinstance(data, str):
        # Replace ${VAR} or $VAR with environment variable value
        def replace_var(match):
            var_name = match.group(1) or match.group(2)
            return os.getenv(var_name, match.group(0))
        return re.sub(r'\$\{([^}]+)\}|\$(\w+)', replace_var, data)
    else:
        return data


def load_providers_config(providers_path: str = "config.yml") -> dict:
    """
    Load providers configuration from unified config.yml.

    Args:
        providers_path: Path to config.yml file (default: config.yml)

    Returns:
        Providers configuration dictionary with default_provider and providers sections

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    try:
        return load_unified_providers(str(providers_path))
    except FileNotFoundError:
        print(f"Error: Config file not found: {providers_path}")
        print(f"Create one from the example: cp config.example.yml config.yml")
        sys.exit(1)


def load_env_vars(env_path: str = ".env", config: dict = None) -> dict:
    """
    Load environment variables.

    Priority:
    1. config.yml smtp section (with ${VAR} substitution already applied)
    2. Environment variables from .env file
    3. Defaults

    Args:
        env_path: Path to .env file
        config: Configuration dict (optional, for SMTP settings)

    Returns:
        Dictionary with environment configuration
    """
    load_dotenv(env_path)

    # Try to get SMTP config from config.yml first, then fall back to env vars
    smtp_config = config.get("smtp", {}) if config else {}

    return {
        "TIMEZONE": os.getenv("TIMEZONE", "Europe/Athens"),
        "SMTP_HOST": smtp_config.get("host") or os.getenv("SMTP_HOST"),
        "SMTP_PORT": smtp_config.get("port") or os.getenv("SMTP_PORT"),
        "SMTP_USER": smtp_config.get("user") or os.getenv("SMTP_USER"),
        "SMTP_PASS": smtp_config.get("password") or os.getenv("SMTP_PASS"),
        "MAIL_TO": smtp_config.get("mail_to") or os.getenv("MAIL_TO"),
        "MAIL_FROM": smtp_config.get("mail_from") or os.getenv("MAIL_FROM"),
        "LOG_RETENTION_DAYS": int(os.getenv("LOG_RETENTION_DAYS", 45)),
        "RUN_RETENTION_DAYS": int(os.getenv("RUN_RETENTION_DAYS", 90)),
        "CACHE_DB_PATH": os.getenv("CACHE_DB_PATH", "./cache/cache.db"),
        "CACHE_TTL_DAYS": int(os.getenv("CACHE_TTL_DAYS", 21)),
    }


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


def main():
    """Main pipeline execution."""
    # Check for --version flag first
    if '--version' in sys.argv:
        print(f"drupal-news version {get_current_version()}")
        sys.exit(0)

    # Parse arguments
    parser = argparse.ArgumentParser(description="Drupal News Aggregator")
    parser.add_argument("--provider", default=None, help="AI provider (openai, anthropic, etc.)")
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument("--days", type=int, default=7, help="Timeframe in days")
    parser.add_argument("--email", choices=["yes", "no"], default="yes", help="Send email")
    parser.add_argument("--dry-run", action="store_true", help="Skip AI and email (testing)")
    parser.add_argument("--use-sources", metavar="DATE", help="Use existing sources from DATE (YYYY-MM-DD), skip fetching")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch and parse sources, skip AI and email")
    parser.add_argument("--config", default="config.yml", help="Config file path (default: config.yml)")
    parser.add_argument("--providers", default="config.yml", help="Providers file path (default: config.yml)")
    parser.add_argument("--env", default=".env", help="Environment file path")
    parser.add_argument("--outdir", default=None, help="Output directory override")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    providers_config = load_providers_config(args.providers)
    env = load_env_vars(args.env, config)

    # Setup
    timezone = env["TIMEZONE"]
    timeframe_days = args.days
    since = days_ago(timeframe_days, timezone)
    run_date = now_in_tz(timezone).strftime("%Y-%m-%d")
    period_label = get_period_label(timeframe_days)

    # Create run directory
    runs_root = Path(args.outdir) if args.outdir else Path(config["run_root"])

    # Check if using existing sources
    use_cached_sources = False
    source_run_dir = None

    if args.use_sources:
        source_date = args.use_sources
        source_run_dir = runs_root / source_date
        sources_file = source_run_dir / "sources.json"

        if not sources_file.exists():
            print(f"Error: Sources file not found: {sources_file}")
            sys.exit(1)

        use_cached_sources = True
        logger_dir = source_run_dir
    else:
        source_run_dir = runs_root / run_date
        logger_dir = source_run_dir

    run_dir = source_run_dir
    ensure_dir(run_dir)

    # Initialize logger
    logger = get_logger(logger_dir, verbose=args.verbose)

    if use_cached_sources:
        logger.info("index", f"Start - Using cached sources from {args.use_sources}")
    else:
        logger.info("index", f"Start - Drupal Newsletter {run_date}")

    start_time = time.time()
    exit_code = EXIT_SUCCESS
    errors = []

    # Initialize variables for metrics (in case of early exit/exception)
    cache = None
    all_items = []
    summary_result = {"provider": "none", "model": "none", "tokens": 0, "cost": 0}

    try:
        # Load or fetch sources
        if use_cached_sources:
            # Load existing sources
            logger.info("sources", f"Loading sources from {source_run_dir}")
            sources_data = safe_read_json(source_run_dir / "sources.json")

            if not sources_data:
                logger.error("sources", "Failed to load sources.json")
                sys.exit(1)

            all_items = sources_data.get("items", [])

            # Extract metadata from cached sources
            metadata = sources_data.get("metadata", {})
            timeframe_days = metadata.get("timeframe_days", args.days)
            timezone = metadata.get("timezone", timezone)
            period_label = get_period_label(timeframe_days)

            logger.info("sources", f"Loaded {len(all_items)} items from cache")

        else:
            # Fetch fresh sources
            # Initialize cache
            cache = CacheManager(env["CACHE_DB_PATH"], env["CACHE_TTL_DAYS"])
            logger.info("cache", "Cache initialized")

            # Fetch content from both RSS feeds and web pages
            logger.info("content_reader", "Fetching content from RSS feeds and web pages...")
            all_items = fetch_content(
                rss_urls=config["sources"]["rss"],
                page_sources=config["sources"]["pages"],
                since=since,
                timezone=timezone,
                cache=cache,
                timeout=config["http"]["timeout_sec"],
                retries=config["http"]["retries"],
                user_agent=config["http"]["user_agent"]
            )
            logger.info("content_reader", f"Fetched {len(all_items)} items")

            # Deduplicate
            all_items = dedupe_items(all_items)
            logger.info("dedupe", f"Total unique items: {len(all_items)}")

            # Validate
            logger.info("validator", "Validating items...")
            validation_report = validate_items(all_items)
            safe_write_json(validation_report, run_dir / "validation_report.json")

            if not validation_report["passed"]:
                logger.warning("validator", f"Validation issues: {len(validation_report['errors'])}")
                exit_code = EXIT_VALIDATION_FAILED
            else:
                logger.info("validator", "Validation passed")

            # Write sources.json
            sources_data = {
                "items": all_items,
                "metadata": {
                    "generated_at": get_iso_timestamp(),
                    "timeframe_days": timeframe_days,
                    "timezone": timezone,
                    "total_items": len(all_items),
                }
            }
            safe_write_json(sources_data, run_dir / "sources.json")

            # Write parsed.md
            logger.info("markdown", "Generating parsed.md...")
            write_parsed_md(
                all_items,
                run_dir / "parsed.md",
                timeframe_days=timeframe_days,
                timezone=timezone,
                max_rows=config["markdown"]["table_max_rows"],
                period_label=period_label
            )

        # Exit early if fetch-only mode
        if args.fetch_only:
            logger.info("index", "Fetch-only mode - stopping before AI summarization")
            logger.info("index", f"Sources saved to: {run_dir}")
            sys.exit(EXIT_SUCCESS)

        # Generate summary
        logger.info("ai_summarizer", "Generating summary...")

        if args.dry_run:
            summary_text = generate_placeholder_summary(all_items, timeframe_days)
            summary_result = {
                "text": summary_text,
                "tokens": 0,
                "model": "dry-run",
                "provider": "none"
            }
        else:
            # Determine provider and model
            provider_name = args.provider or providers_config.get("default_provider", "openai")
            provider_config = providers_config["providers"].get(provider_name)

            if not provider_config:
                logger.error("ai_summarizer", f"Provider {provider_name} not found")
                exit_code = EXIT_SUMMARIZER_FAILED
                raise ValueError(f"Provider {provider_name} not configured")

            model_name = args.model or provider_config["model"]

            try:
                summary_result = summarize(
                    items=all_items,
                    provider=provider_name,
                    model=model_name,
                    temperature=provider_config.get("temperature", 0.2),
                    timeframe_days=timeframe_days,
                    timezone=timezone,
                    provider_config=provider_config
                )

                summary_text = summary_result["text"]
                logger.info("ai_summarizer",
                           f"Summary generated: {summary_result['tokens']} tokens, "
                           f"{summary_result.get('duration', 0):.1f}s")

            except Exception as e:
                logger.error("ai_summarizer", f"Summarization failed: {e}")
                errors.append(str(e))
                exit_code = EXIT_SUMMARIZER_FAILED
                raise

        # Validate summary
        summary_validation = validate_summary(summary_text, all_items)
        if not summary_validation["passed"]:
            logger.warning("validator", "Summary validation issues")

        # Write summary.md
        metadata = {
            "date": run_date,
            "timeframe_days": timeframe_days,
            "timezone": timezone,
            "provider": summary_result.get("provider", "unknown"),
            "model": summary_result.get("model", "unknown"),
            "generated_at": get_iso_timestamp(),
            "period_label": period_label
        }
        write_summary_md(summary_text, run_dir / "summary.md", metadata)

        # Generate PDF
        logger.info("pdf", "Generating PDF...")
        pdf_path = generate_summary_pdf(run_dir, period_label=period_label)
        if pdf_path:
            logger.info("pdf", f"PDF generated: {pdf_path.name}")
        else:
            logger.warning("pdf", "PDF generation failed")

        # Send email
        if args.email == "yes" and not args.dry_run:
            logger.info("email", "Sending email...")
            email_sent = send_report(
                config,
                env,
                run_date,
                run_dir / "summary.md",
                timezone,
                period_label
            )

            if email_sent:
                logger.info("email", f"Email sent to {env['MAIL_TO']}")
            else:
                logger.error("email", "Email sending failed")
                errors.append("Email sending failed")
                exit_code = EXIT_EMAIL_FAILED

            # Write email log
            attachment_name = pdf_path.name if pdf_path and pdf_path.exists() else "summary.md"
            write_email_log(
                run_dir / "email.txt",
                f"{config['email']['subject_prefix']} {run_date}",
                f"Drupal {period_label} for {run_date}",
                env["MAIL_TO"],
                email_sent,
                attachment_name
            )
        else:
            logger.info("email", "Email skipped")

        # Verify integrity
        logger.info("integrity", "Verifying run integrity...")
        if verify_run_simple(run_dir):
            logger.success("integrity", "Integrity check passed")
        else:
            logger.error("integrity", "Integrity check failed")
            exit_code = EXIT_INTEGRITY_FAILED

        # Cleanup old data
        logger.info("cleanup", "Running cleanup...")
        cleanup_results = run_cleanup(
            runs_root,
            Path(env["CACHE_DB_PATH"]),
            env["RUN_RETENTION_DAYS"],
            env["LOG_RETENTION_DAYS"],
            env["CACHE_TTL_DAYS"]
        )
        logger.info("cleanup", f"Cleaned: {cleanup_results['runs']['deleted']} runs, "
                              f"{cleanup_results['logs_deleted']} logs, "
                              f"{cleanup_results['cache_purged']} cache entries")

    except KeyboardInterrupt:
        logger.error("index", "Interrupted by user")
        exit_code = 1
    except Exception as e:
        logger.error("index", f"Pipeline failed: {e}")
        errors.append(str(e))
        if exit_code == EXIT_SUCCESS:
            exit_code = 1
    finally:
        # Always collect metrics, even on failure or early exit
        duration = time.time() - start_time

        # Get cache stats if cache exists
        cache_stats = {"valid": 0, "expired": 0, "total": 0}
        if cache is not None:
            try:
                cache_stats = cache.get_stats()
            except Exception:
                pass  # Use default empty stats

        # Collect and save metrics
        try:
            metrics = collect_metrics(
                run_dir,
                summary_result.get("provider", "none"),
                summary_result.get("model", "none"),
                duration,
                all_items,
                summary_result,
                exit_code,
                cache_stats,
                errors
            )
            logger.info("metrics", f"Metrics collected: {duration:.1f}s, {len(all_items)} items")
        except Exception as e:
            logger.error("metrics", f"Failed to collect metrics: {e}")

    # Final log
    duration = time.time() - start_time
    logger.info("index", f"Finished - exit_code={exit_code}, duration={duration:.1f}s")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
