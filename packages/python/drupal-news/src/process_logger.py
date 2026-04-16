"""Process logger for Drupal Aggregator using loguru."""
from pathlib import Path
from typing import Optional
from loguru import logger
import sys


class ProcessLogger:
    """Structured logging for pipeline execution."""

    def __init__(self, run_dir: Path, verbose: bool = False):
        """
        Initialize process logger.

        Args:
            run_dir: Directory for this run's logs
            verbose: If True, also log to console
        """
        self.run_dir = Path(run_dir)
        self.log_file = self.run_dir / "run.log"
        self.verbose = verbose

        # Remove default handler
        logger.remove()

        # Add file handler
        logger.add(
            self.log_file,
            format="{time:YYYY-MM-DDTHH:mm:ss} [{extra[component]}] {message}",
            level="INFO"
        )

        # Add console handler if verbose
        if verbose:
            logger.add(
                sys.stdout,
                format="<green>{time:HH:mm:ss}</green> <level>[{extra[component]}]</level> {message}",
                level="INFO",
                colorize=True
            )

    def log(self, component: str, message: str, level: str = "INFO"):
        """
        Log a message with component context.

        Args:
            component: Component name (e.g., 'rss_reader', 'validator')
            message: Log message
            level: Log level (INFO, WARNING, ERROR)
        """
        log_func = getattr(logger.bind(component=component), level.lower())
        log_func(message)

    def info(self, component: str, message: str):
        """Log info message."""
        self.log(component, message, "INFO")

    def warning(self, component: str, message: str):
        """Log warning message."""
        self.log(component, message, "WARNING")

    def error(self, component: str, message: str):
        """Log error message."""
        self.log(component, message, "ERROR")

    def success(self, component: str, message: str):
        """Log success message."""
        self.log(component, message, "SUCCESS")


def get_logger(run_dir: Path, verbose: bool = False) -> ProcessLogger:
    """
    Get or create process logger for a run.

    Args:
        run_dir: Directory for this run
        verbose: Enable console output

    Returns:
        ProcessLogger instance
    """
    return ProcessLogger(run_dir, verbose)
