"""Pipeline integrity checker for Drupal Aggregator."""
from pathlib import Path
from typing import Dict, List
import json


def verify_run(run_dir: Path) -> Dict[str, bool]:
    """
    Verify that all required outputs exist and are valid.

    Args:
        run_dir: Run directory to verify

    Returns:
        Dictionary with verification results
    """
    run_dir = Path(run_dir)

    checks = {
        "parsed_md_exists": False,
        "summary_md_exists": False,
        "sources_json_exists": False,
        "validation_json_exists": False,
        "metrics_json_exists": False,
        "run_log_exists": False,
        "parsed_md_not_empty": False,
        "summary_md_not_empty": False,
        "sources_json_valid": False,
        "validation_json_valid": False,
        "metrics_json_valid": False,
    }

    # Check file existence
    parsed_md = run_dir / "parsed.md"
    summary_md = run_dir / "summary.md"
    sources_json = run_dir / "sources.json"
    validation_json = run_dir / "validation_report.json"
    metrics_json = run_dir / "metrics.json"
    run_log = run_dir / "run.log"

    checks["parsed_md_exists"] = parsed_md.exists()
    checks["summary_md_exists"] = summary_md.exists()
    checks["sources_json_exists"] = sources_json.exists()
    checks["validation_json_exists"] = validation_json.exists()
    checks["metrics_json_exists"] = metrics_json.exists()
    checks["run_log_exists"] = run_log.exists()

    # Check content validity
    if checks["parsed_md_exists"]:
        checks["parsed_md_not_empty"] = parsed_md.stat().st_size > 100

    if checks["summary_md_exists"]:
        checks["summary_md_not_empty"] = summary_md.stat().st_size > 100

    if checks["sources_json_exists"]:
        checks["sources_json_valid"] = _is_valid_json(sources_json)

    if checks["validation_json_exists"]:
        checks["validation_json_valid"] = _is_valid_json(validation_json)

    if checks["metrics_json_exists"]:
        checks["metrics_json_valid"] = _is_valid_json(metrics_json)

    return checks


def _is_valid_json(filepath: Path) -> bool:
    """Check if file contains valid JSON."""
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except Exception:
        return False


def verify_run_simple(run_dir: Path) -> bool:
    """
    Simple verification - returns True if all critical files exist.

    Args:
        run_dir: Run directory

    Returns:
        True if all critical files exist
    """
    checks = verify_run(run_dir)

    required = [
        "parsed_md_exists",
        "summary_md_exists",
        "metrics_json_exists",
        "run_log_exists",
        "parsed_md_not_empty",
        "summary_md_not_empty"
    ]

    return all(checks.get(key, False) for key in required)


def generate_integrity_report(run_dir: Path) -> Dict:
    """
    Generate detailed integrity report.

    Args:
        run_dir: Run directory

    Returns:
        Report dictionary
    """
    checks = verify_run(run_dir)

    passed_count = sum(1 for v in checks.values() if v)
    total_count = len(checks)

    report = {
        "run_dir": str(run_dir),
        "passed": verify_run_simple(run_dir),
        "checks": checks,
        "passed_count": passed_count,
        "total_count": total_count,
        "pass_rate": round(passed_count / total_count * 100, 1)
    }

    return report


def check_all_runs(runs_root: Path, last_n: int = 10) -> List[Dict]:
    """
    Check integrity of last N runs.

    Args:
        runs_root: Runs root directory
        last_n: Number of recent runs to check

    Returns:
        List of report dictionaries
    """
    runs_root = Path(runs_root)

    if not runs_root.exists():
        return []

    run_dirs = sorted(runs_root.glob("*"), reverse=True)[:last_n]
    reports = []

    for run_dir in run_dirs:
        if run_dir.is_dir():
            report = generate_integrity_report(run_dir)
            reports.append(report)

    return reports
