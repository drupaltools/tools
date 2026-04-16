"""Data cleaner for Drupal Newsletter."""
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import gzip
from typing import List, Dict


def cleanup_old_runs(
    runs_root: Path,
    retention_days: int = 90,
    compress: bool = True
) -> Dict[str, int]:
    """
    Remove or compress old run directories.

    Args:
        runs_root: Root directory containing runs
        retention_days: Number of days to retain
        compress: Whether to compress before deletion

    Returns:
        Dictionary with cleanup stats
    """
    runs_root = Path(runs_root)
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    deleted_count = 0
    compressed_count = 0
    errors = []

    if not runs_root.exists():
        return {"deleted": 0, "compressed": 0, "errors": []}

    for run_dir in runs_root.glob("*"):
        if not run_dir.is_dir():
            continue

        try:
            # Parse directory name (YYYY-MM-DD format)
            dir_name = run_dir.name
            run_date = datetime.strptime(dir_name, "%Y-%m-%d")

            if run_date < cutoff_date:
                if compress:
                    # Compress before deletion
                    archive_path = run_dir.parent / f"{dir_name}.tar.gz"
                    if not archive_path.exists():
                        _compress_directory(run_dir, archive_path)
                        compressed_count += 1

                # Delete directory
                shutil.rmtree(run_dir)
                deleted_count += 1

        except ValueError:
            # Invalid directory name format
            continue
        except Exception as e:
            errors.append(f"Error processing {run_dir}: {e}")

    return {
        "deleted": deleted_count,
        "compressed": compressed_count,
        "errors": errors
    }


def cleanup_old_logs(
    runs_root: Path,
    retention_days: int = 45
) -> int:
    """
    Remove old log files.

    Args:
        runs_root: Root directory containing runs
        retention_days: Number of days to retain logs

    Returns:
        Number of logs deleted
    """
    runs_root = Path(runs_root)
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    deleted_count = 0

    if not runs_root.exists():
        return 0

    for run_dir in runs_root.glob("*"):
        if not run_dir.is_dir():
            continue

        try:
            dir_name = run_dir.name
            run_date = datetime.strptime(dir_name, "%Y-%m-%d")

            if run_date < cutoff_date:
                log_file = run_dir / "run.log"
                if log_file.exists():
                    log_file.unlink()
                    deleted_count += 1

        except (ValueError, OSError):
            continue

    return deleted_count


def cleanup_cache(cache_db_path: Path, ttl_days: int = 21) -> int:
    """
    Purge expired cache entries.

    Args:
        cache_db_path: Path to cache database
        ttl_days: Time-to-live in days

    Returns:
        Number of entries purged
    """
    from drupal_news.cache_manager import CacheManager

    cache = CacheManager(str(cache_db_path), ttl_days)
    return cache.purge_expired()


def _compress_directory(source_dir: Path, output_path: Path):
    """Compress directory to tar.gz."""
    import tarfile

    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(source_dir, arcname=source_dir.name)


def run_cleanup(
    runs_root: Path,
    cache_db_path: Path,
    run_retention_days: int = 90,
    log_retention_days: int = 45,
    cache_ttl_days: int = 21
) -> Dict[str, any]:
    """
    Run all cleanup tasks.

    Args:
        runs_root: Runs directory
        cache_db_path: Cache database path
        run_retention_days: Days to retain runs
        log_retention_days: Days to retain logs
        cache_ttl_days: Cache TTL in days

    Returns:
        Dictionary with all cleanup results
    """
    results = {}

    # Cleanup old runs
    results["runs"] = cleanup_old_runs(runs_root, run_retention_days)

    # Cleanup old logs
    results["logs_deleted"] = cleanup_old_logs(runs_root, log_retention_days)

    # Cleanup cache
    results["cache_purged"] = cleanup_cache(cache_db_path, cache_ttl_days)

    return results
