#!/usr/bin/env python3
"""
Scheduler wrapper for Drupal News Aggregator.
This wrapper adds the src directory to the path and runs the scheduler module.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the main function from src.scheduler
from scheduler import main

if __name__ == "__main__":
    main()
