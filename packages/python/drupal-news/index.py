#!/usr/bin/env python3
"""
Main entry point for Drupal News Aggregator.
This wrapper adds the src directory to the path and runs the main index module.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the main function from src.index
from index import main

if __name__ == "__main__":
    main()
