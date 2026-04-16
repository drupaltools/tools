# Release Process

This monorepo uses [Changesets](https://github.com/changesets/changesets) to manage independent versioning and releases across all language ecosystems.

## Overview

- Each package has its own version (`package.json`, `Cargo.toml`, `pyproject.toml`, etc.)
- Only changed packages get new versions
- Changesets generates a PR that bumps versions and updates changelogs
- Publishing happens automatically when the version PR is merged

## Workflow

### Step 1: Develop

Make your changes in a feature branch. Follow [CONTRIBUTING.md](./CONTRIBUTING.md) for code quality standards.

### Step 2: Create a Changeset

```bash
pnpm changeset
```

This interactive command creates a `.md` file in `.changeset/`:

```markdown
---
'@monorepo/example-package': minor
---

Add new feature for processing strings
```

### Step 3: Open a PR

Push your branch and open a PR:

- Add the changeset file
- Your changes must pass all CI checks
- Maintainers review and approve

### Step 4: Changesets Version PR

When the PR is merged to `main`, Changesets:

1. Bumps versions of changed packages
2. Generates/updates `CHANGELOG.md` per package
3. Opens an automatic PR with all version changes

### Step 5: Publish

When the version PR is merged:

- CI automatically publishes each package to its registry
- npm packages → npmjs.com
- PHP packages → Packagist
- Python packages → PyPI
- Go modules → pkg.go.dev
- Rust crates → crates.io

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):

| Change Type | Example                         | Version Bump      |
| ----------- | ------------------------------- | ----------------- |
| Major       | Breaking API change             | `1.0.0` → `2.0.0` |
| Minor       | New backward-compatible feature | `1.0.0` → `1.1.0` |
| Patch       | Backward-compatible fix         | `1.0.0` → `1.0.1` |

## Managing Changesets

### View pending changesets

```bash
pnpm changeset status
```

### Remove a changeset (before PR merge)

```bash
pnpm changeset remove @monorepo/package-name
```

### Bump versions locally (dry run)

```bash
pnpm changeset version
```

### Publish locally (for testing)

```bash
pnpm turbo run build
pnpm changeset publish
```

## Private Packages

For packages that shouldn't be published to public registries:

1. Set `"private": true` in `package.json` (JS)
2. Add to `.changeset/config.json` `ignore` array
3. Skip CI publish jobs for that package path

## Manual Releases

For emergency releases or registry issues:

```bash
# 1. Tag manually
git tag v1.0.0 packages/js/example-package

# 2. Build and publish
cd packages/js/example-package
npm publish --access public

# 3. Push tag
git push origin v1.0.0
```

## Troubleshooting

### "No changeset found"

Run `pnpm changeset` before merging to `main` if you want a version bump.

### Publish failed

Check the CI logs for specific errors. Common issues:

- `NPM_TOKEN` not set or expired
- Package name already taken
- Version already published

### Wrong version bumped

Use `pnpm changeset version` to interactively adjust versions before the version PR.

## Registry Configuration

| Registry  | Token Secret                | Variable               |
| --------- | --------------------------- | ---------------------- |
| npm       | `NPM_TOKEN`                 | `registry` in `.npmrc` |
| Packagist | `PACKAGIST_TOKEN`           | Configured in workflow |
| PyPI      | `PYPI_TOKEN`                | `uv publish --token`   |
| crates.io | `CARGO_REGISTRY_TOKEN`      | `~/.cargo/credentials` |
| Go        | GitHub Actions auto-publish | `GITHUB_TOKEN`         |
