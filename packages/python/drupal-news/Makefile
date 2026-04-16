.PHONY: help install scss scss-watch viewer clean

help:
	@echo "Drupal News - Available Commands"
	@echo ""
	@echo "  make install     - Install all dependencies"
	@echo "  make scss        - Compile SCSS to CSS (one-time)"
	@echo "  make scss-watch  - Watch SCSS files and auto-compile"
	@echo "  make viewer      - Start web viewer (port 5000)"
	@echo "  make clean       - Remove generated CSS files"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

scss:
	@echo "Compiling SCSS to CSS..."
	python3 src/compile_scss.py

scss-watch:
	@echo "Starting SCSS watcher..."
	python3 src/compile_scss.py --watch

viewer: scss
	@echo "Starting web viewer on http://localhost:5000"
	python3 viewer.py

clean:
	@echo "Cleaning generated CSS files..."
	rm -rf static/css/*.css
	@echo "Done!"
