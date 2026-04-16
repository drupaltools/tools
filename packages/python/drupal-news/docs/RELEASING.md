# Release Process

This document describes how to create and publish new releases of Drupal News Aggregator.

## Prerequisites

- Git repository with clean working tree
- Write access to the repository
- PyPI API token configured in GitHub secrets (for automated publishing)

## Quick Release

The `release.sh` script automates the entire release process:

```bash
# Patch release (0.1.0 → 0.1.1)
./release.sh patch -m "Bug fixes and improvements"

# Minor release (0.1.0 → 0.2.0)
./release.sh minor -m "New features added"

# Major release (0.1.0 → 1.0.0)
./release.sh major -m "Breaking changes"

# Specific version
./release.sh 1.2.3 -m "Custom version release"

# Create and push in one step
./release.sh patch -m "Bug fixes" --push
```

## Release Script Details

### What it does

1. ✓ Validates git repository state (clean working tree)
2. ✓ Checks current branch (warns if not main/master)
3. ✓ Updates VERSION file
4. ✓ Updates RELEASES.md with changelog
5. ✓ Creates git commit
6. ✓ Creates annotated git tag
7. ✓ Optionally pushes to remote

### Options

```bash
./release.sh [OPTIONS] <VERSION_TYPE>

VERSION_TYPE:
  major          Increment major version (X.0.0)
  minor          Increment minor version (0.X.0)
  patch          Increment patch version (0.0.X)
  <version>      Use specific version (e.g., 1.2.3)

OPTIONS:
  -m, --message  Release message/changelog
  -p, --push     Push tag to remote after creating
  -h, --help     Show help
```

### Interactive Mode

If you don't provide `-m`, the script will prompt for changelog:

```bash
./release.sh patch
# Enter release notes/changelog (Ctrl+D when done):
# - Fixed bug in RSS parser
# - Improved error handling
# [Ctrl+D]
```

## Manual Release Process

If you prefer manual control:

### 1. Update VERSION

```bash
echo "0.2.0" > VERSION
```

### 2. Update RELEASES.md

Add entry at the top:

```markdown
## [0.2.0] - 2025-10-30

### Added

- New feature X
- New feature Y

### Fixed

- Bug fix A
- Bug fix B
```

### 3. Commit and Tag

```bash
git add VERSION RELEASES.md
git commit -m "Release v0.2.0"
git tag -a v0.2.0 -m "Release v0.2.0"
```

### 4. Push

```bash
git push origin main
git push origin v0.2.0
```

## Automated Publishing

When you push a version tag (e.g., `v0.2.0`), GitHub Actions automatically:

1. Builds the package
2. Runs quality checks
3. Publishes to PyPI
4. Creates GitHub Release with changelog

### Monitor the Build

Check build status at:

```
https://github.com/drupaltools/tools/actions
```

### Verify Publication

Package will be available at:

```
https://pypi.org/project/drupal-news/
```

## GitHub Secrets Setup

For automated PyPI publishing, configure this secret in GitHub:

**Repository → Settings → Secrets → Actions → New secret**

- Name: `PYPI_API_TOKEN`
- Value: Your PyPI API token from https://pypi.org/manage/account/token/

### Generate PyPI Token

1. Go to https://pypi.org/manage/account/token/
2. Create token with scope: "Entire account" or "Project: drupal-news"
3. Copy token (starts with `pypi-`)
4. Add to GitHub secrets

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major (X.0.0)**: Breaking changes
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, backward compatible

### Examples

```
0.1.0 → 0.1.1  (patch: bug fixes)
0.1.1 → 0.2.0  (minor: new features)
0.2.0 → 1.0.0  (major: breaking changes)
```

## RELEASES.md Format

Use [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [VERSION] - YYYY-MM-DD

### Added

- New features

### Changed

- Changes to existing functionality

### Deprecated

- Soon-to-be removed features

### Removed

- Removed features

### Fixed

- Bug fixes

### Security

- Security improvements
```

## Rollback a Release

If something goes wrong:

### 1. Delete Remote Tag

```bash
git push --delete origin v0.2.0
```

### 2. Delete Local Tag

```bash
git tag -d v0.2.0
```

### 3. Revert Commit

```bash
git revert HEAD
git push origin main
```

### 4. Delete PyPI Release

PyPI releases cannot be deleted, but you can:

- Yank the release (marks it as unavailable)
- Upload a fixed version immediately

## Testing Before Release

### Local Build Test

```bash
# Build package
python -m build

# Install locally
pip install dist/drupal_news-*.whl

# Test commands
drupal-news --help
drupal-news --dry-run
```

### Test Installation from TestPyPI

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ drupal-news

# Test
drupal-news --help
drupal-news --version  # Should show the new version
drupal-news-scheduler --version  # Should show the new version
drupal-news-email --version  # Should show the new version
drupal-news-viewer --version  # Should show the new version
```

## Release Checklist

Before creating a release:

- [ ] All tests passing
- [ ] Documentation updated
- [ ] RELEASES.md prepared with changelog
- [ ] VERSION file ready to update
- [ ] Working tree is clean
- [ ] On correct branch (main/master)

After release:

- [ ] Tag pushed to GitHub
- [ ] GitHub Actions build succeeded
- [ ] Package available on PyPI
- [ ] GitHub Release created
- [ ] Documentation reflects new version

## Troubleshooting

### "Working directory is not clean"

Commit or stash your changes:

```bash
git status
git add .
git commit -m "Prepare for release"
```

### "Not on main/master branch"

Either checkout main/master or use the interactive prompt to continue anyway.

### GitHub Actions fails

1. Check Actions tab for error logs
2. Common issues:
   - PYPI_API_TOKEN not set or expired
   - VERSION mismatch between file and tag
   - Build dependencies missing

### Package build fails

```bash
# Clean and rebuild
rm -rf dist/ build/ *.egg-info
python -m build
```

## Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
