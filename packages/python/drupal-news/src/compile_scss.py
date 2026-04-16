#!/usr/bin/env python3
"""
Simple SCSS compiler for Drupal News viewer.

Compiles SCSS files from static/scss/ to static/css/
"""

import os
import sys
from pathlib import Path
import sass
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SCSSCompiler:
    """SCSS to CSS compiler."""

    def __init__(self, scss_dir="static/scss", css_dir="static/css"):
        self.scss_dir = Path(scss_dir)
        self.css_dir = Path(css_dir)

        # Create output directory if it doesn't exist
        self.css_dir.mkdir(parents=True, exist_ok=True)

    def compile_file(self, scss_file):
        """Compile a single SCSS file to CSS."""
        scss_path = Path(scss_file)

        # Skip partials (files starting with _)
        if scss_path.name.startswith('_'):
            return

        # Determine output path
        relative_path = scss_path.relative_to(self.scss_dir)
        css_path = self.css_dir / relative_path.with_suffix('.css')

        try:
            # Compile SCSS to CSS
            css_content = sass.compile(
                filename=str(scss_path),
                output_style='compressed',
                precision=10
            )

            # Write CSS file
            css_path.parent.mkdir(parents=True, exist_ok=True)
            css_path.write_text(css_content)

            print(f"✓ Compiled: {scss_path} -> {css_path}")

        except sass.CompileError as e:
            print(f"✗ Error compiling {scss_path}:")
            print(f"  {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Unexpected error compiling {scss_path}:")
            print(f"  {e}")
            sys.exit(1)

    def compile_all(self):
        """Compile all SCSS files in the source directory."""
        scss_files = list(self.scss_dir.glob('**/*.scss'))

        if not scss_files:
            print(f"No SCSS files found in {self.scss_dir}")
            return

        print(f"Compiling {len(scss_files)} SCSS file(s)...")

        for scss_file in scss_files:
            self.compile_file(scss_file)

        print(f"\n✓ All files compiled successfully!")


class SCSSWatcher(FileSystemEventHandler):
    """Watch for SCSS file changes and recompile."""

    def __init__(self, compiler):
        self.compiler = compiler
        self.last_modified = {}

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory or not event.src_path.endswith('.scss'):
            return

        # Debounce - avoid multiple rapid recompiles
        path = event.src_path
        now = time.time()

        if path in self.last_modified:
            if now - self.last_modified[path] < 0.5:
                return

        self.last_modified[path] = now

        print(f"\n→ Change detected: {path}")
        self.compiler.compile_all()


def watch_mode(compiler):
    """Watch SCSS directory for changes and recompile."""
    print(f"Watching {compiler.scss_dir} for changes...")
    print("Press Ctrl+C to stop\n")

    event_handler = SCSSWatcher(compiler)
    observer = Observer()
    observer.schedule(event_handler, str(compiler.scss_dir), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping watcher...")
        observer.stop()

    observer.join()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Compile SCSS files to CSS for Drupal News viewer'
    )
    parser.add_argument(
        '--watch',
        '-w',
        action='store_true',
        help='Watch for changes and recompile automatically'
    )
    parser.add_argument(
        '--scss-dir',
        default='static/scss',
        help='Source SCSS directory (default: static/scss)'
    )
    parser.add_argument(
        '--css-dir',
        default='static/css',
        help='Output CSS directory (default: static/css)'
    )

    args = parser.parse_args()

    compiler = SCSSCompiler(args.scss_dir, args.css_dir)

    # Initial compilation
    compiler.compile_all()

    # Watch mode if requested
    if args.watch:
        watch_mode(compiler)


if __name__ == '__main__':
    main()
