# PyPI Packaging Guide

This guide explains how to build and publish the Drupal News package to PyPI.

## Prerequisites

1. **Python 3.10+** installed
2. **PyPI account** at https://pypi.org
3. **TestPyPI account** at https://test.pypi.org (for testing)
4. **API tokens** for both PyPI and TestPyPI

## Setup API Tokens

### 1. Create PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Save it securely

### 2. Configure pip

Create or edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

## Package Structure

```
drupal-news/
├── src/                      # Source code (becomes drupal_news package)
│   ├── __init__.py
│   ├── cli.py               # CLI entry points
│   ├── index.py             # Main aggregator
│   ├── scheduler.py         # Scheduler
│   ├── send_email.py        # Email sender
│   └── utils/               # Utility modules
├── static/                  # Web viewer assets
├── docs/                    # Documentation
├── pyproject.toml           # Package metadata (PEP 621)
├── MANIFEST.in              # Additional files to include
├── VERSION                  # Version number
├── LICENSE                  # GPL-2.0 license
├── README.md               # PyPI description
└── build_package.py        # Build script
```

## Build Script Usage

### Quick Start

```bash
# Full release workflow
python3 build_package.py --release
```

This runs all checks and prepares the package for upload.

### Individual Steps

```bash
# 1. Clean build artifacts
python3 build_package.py --clean

# 2. Build package
python3 build_package.py --build

# 3. Check package quality
python3 build_package.py --check

# 4. Test local install
python3 build_package.py --test

# 5. Upload to TestPyPI
python3 build_package.py --test-upload

# 6. Upload to production PyPI
python3 build_package.py --upload
```

### Version Management

```bash
# Set version before building
python3 build_package.py --version 1.0.0

# Then build
python3 build_package.py --build
```

## Release Workflow

### 1. Pre-Release Checklist

- [ ] All tests pass
- [ ] Documentation is up to date
- [ ] CHANGELOG.md updated
- [ ] Version bumped in VERSION file
- [ ] Git committed and tagged

### 2. Test Build Locally

```bash
# Clean previous builds
python3 build_package.py --clean

# Build package
python3 build_package.py --build

# Check package quality
python3 build_package.py --check

# Test installation
python3 build_package.py --test
```

### 3. Test on TestPyPI

```bash
# Upload to TestPyPI
python3 build_package.py --test-upload

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ drupal-news

# Test the installation
drupal-news --help
```

### 4. Production Release

```bash
# Upload to PyPI (production)
python3 build_package.py --upload

# Verify on PyPI
# Visit: https://pypi.org/project/drupal-news/
```

### 5. Post-Release

```bash
# Tag the release in git
git tag v1.0.0
git push origin v1.0.0

# Create GitHub release (optional)
gh release create v1.0.0 --notes "Release notes here"
```

## Package Entry Points

The package provides four command-line tools:

### 1. `drupal-news` (main aggregator)

```bash
drupal-news --provider openai --days 7
```

### 2. `drupal-news-scheduler` (scheduler)

```bash
drupal-news-scheduler --every friday --hour 9 --provider openai
```

### 3. `drupal-news-email` (email sender)

```bash
drupal-news-email --latest --days 7
```

### 4. `drupal-news-viewer` (web viewer)

```bash
drupal-news-viewer
# Opens http://localhost:5000
```

## Installation for End Users

### Basic Installation

```bash
pip install drupal-news
```

### With AI Provider Support

```bash
# OpenAI support
pip install drupal-news[openai]

# Anthropic support
pip install drupal-news[anthropic]

# Google Gemini support
pip install drupal-news[google]

# All providers
pip install drupal-news[all-providers]
```

### Development Installation

```bash
# Clone repository
git clone https://github.com/drupaltools/tools.git
cd drupal-news

# Install in development mode
pip install -e ".[dev]"
```

## Configuration After Installation

### 1. Create Configuration Directory

```bash
mkdir -p ~/.drupal-news
cd ~/.drupal-news
```

### 2. Create `.env` File

```bash
# Copy example
curl -O https://raw.githubusercontent.com/yourusername/drupal-news/main/.env.example

# Edit with your settings
nano .env
```

### 3. Create `config.json`

```bash
# Download example
curl -O https://raw.githubusercontent.com/yourusername/drupal-news/main/config.example.json
mv config.example.json config.json

# Edit as needed
nano config.json
```

### 4. Run First Collection

```bash
drupal-news --fetch-only --days 7
```

## Troubleshooting

### Build Fails

**Problem**: `build` command fails

**Solutions**:

```bash
# Ensure build tools are installed
pip install --upgrade build twine

# Clean and retry
python3 build_package.py --clean
python3 build_package.py --build
```

### Upload Fails

**Problem**: `twine upload` authentication fails

**Solutions**:

- Verify API token in `~/.pypirc`
- Check token has upload permissions
- Ensure using `__token__` as username

### Package Name Conflict

**Problem**: Package name already taken on PyPI

**Solutions**:

- Choose a different name in `pyproject.toml`
- Use organization namespace: `org-drupal-news`

### Import Errors After Install

**Problem**: Cannot import modules after install

**Solutions**:

```bash
# Verify package installed
pip show drupal-news

# Check package structure
python3 -c "import drupal_news; print(drupal_news.__file__)"

# Reinstall
pip install --force-reinstall drupal-news
```

## Advanced Topics

### Custom Package Index

To host on a private PyPI server:

```bash
# Upload to custom index
python3 -m twine upload \
  --repository-url https://your-pypi.server.com \
  dist/*
```

### Automated Releases with GitHub Actions

See `.github/workflows/release.yml` for automated release on git tags.

### Version Management Strategies

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

```bash
# Bug fix release
python3 build_package.py --version 1.0.1

# New feature release
python3 build_package.py --version 1.1.0

# Breaking change release
python3 build_package.py --version 2.0.0
```

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [PEP 621 (pyproject.toml)](https://peps.python.org/pep-0621/)
- [TestPyPI](https://test.pypi.org/)
- [Twine Documentation](https://twine.readthedocs.io/)

## Support

For issues or questions:

- GitHub Issues: https://github.com/drupaltools/tools/issues
- Documentation: https://github.com/drupaltools/tools#readme
