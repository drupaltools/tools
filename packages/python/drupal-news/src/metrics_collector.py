"""Metrics collector for Drupal Aggregator."""
from pathlib import Path
from typing import Dict, Any, List
from drupal_news.utils.consolidated_utils import safe_write_json, get_iso_timestamp


def collect_metrics(
    run_dir: Path,
    provider: str,
    model: str,
    duration_s: float,
    items: List[Dict[str, Any]],
    summary_result: Dict[str, Any],
    exit_code: int,
    cache_stats: Dict[str, int] = None,
    errors: List[str] = None
) -> Dict[str, Any]:
    """
    Collect and save run metrics.

    Args:
        run_dir: Run directory path
        provider: AI provider used
        model: Model name used
        duration_s: Total duration in seconds
        items: List of collected items
        summary_result: Summary generation result
        exit_code: Pipeline exit code
        cache_stats: Optional cache statistics
        errors: Optional list of errors

    Returns:
        Metrics dictionary
    """
    metrics = {
        "timestamp": get_iso_timestamp(),
        "provider": provider,
        "model": model,
        "duration_s": round(duration_s, 2),
        "items_total": len(items),
        "items_rss": sum(1 for item in items if item.get("source_type") == "rss"),
        "items_page": sum(1 for item in items if item.get("source_type") == "page"),
        "tokens_used": summary_result.get("tokens", 0),
        "ai_cost_usd": round(float(summary_result.get("cost", 0.0)), 6),
        "exit_code": exit_code
    }

    # Add cache stats if provided
    if cache_stats:
        metrics["cache_hits"] = cache_stats.get("valid", 0)
        metrics["cache_misses"] = cache_stats.get("expired", 0)
        metrics["cache_total"] = cache_stats.get("total", 0)

    # Add errors if provided
    if errors:
        metrics["errors"] = errors[:10]  # Limit to first 10

    # Write to file
    metrics_path = run_dir / "metrics.json"
    safe_write_json(metrics, metrics_path)

    return metrics


def aggregate_metrics(runs_dir: Path, last_n: int = 30) -> Dict[str, Any]:
    """
    Aggregate metrics from last N runs.

    Args:
        runs_dir: Runs directory
        last_n: Number of runs to aggregate

    Returns:
        Aggregated metrics
    """
    run_dirs = sorted(Path(runs_dir).glob("*"), reverse=True)[:last_n]

    total_runs = 0
    total_items = 0
    total_tokens = 0
    total_duration = 0
    success_count = 0
    providers_used = {}

    for run_dir in run_dirs:
        metrics_path = run_dir / "metrics.json"

        if not metrics_path.exists():
            continue

        try:
            import json
            with open(metrics_path) as f:
                metrics = json.load(f)

            total_runs += 1
            total_items += metrics.get("items_total", 0)
            total_tokens += metrics.get("tokens_used", 0)
            total_duration += metrics.get("duration_s", 0)

            if metrics.get("exit_code") == 0:
                success_count += 1

            provider = metrics.get("provider", "unknown")
            providers_used[provider] = providers_used.get(provider, 0) + 1

        except Exception:
            continue

    return {
        "total_runs": total_runs,
        "success_rate": round(success_count / total_runs * 100, 1) if total_runs > 0 else 0,
        "avg_items_per_run": round(total_items / total_runs, 1) if total_runs > 0 else 0,
        "avg_tokens_per_run": round(total_tokens / total_runs, 1) if total_runs > 0 else 0,
        "avg_duration_s": round(total_duration / total_runs, 1) if total_runs > 0 else 0,
        "providers_used": providers_used,
        "last_n_runs": last_n
    }
