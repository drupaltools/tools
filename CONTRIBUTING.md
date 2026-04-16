# Contributing to the Monorepo

Thank you for contributing! This monorepo supports packages in PHP, JavaScript/TypeScript, Python, Go, and Rust. Follow these guidelines to add or modify packages.

## Table of Contents

- [Quick Start](#quick-start)
- [Adding a New Package](#adding-a-new-package)
- [Development Setup](#development-setup)
- [Package Scripts](#package-scripts)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Commit Messages](#commit-messages)
- [Release Process](#release-process)

## Quick Start

```bash
# Clone and install
git clone <repo-url>
cd monorepo
pnpm install

# Run all tests
pnpm test

# Run all lints
pnpm lint

# Build all packages
pnpm build
```

## Adding a New Package

### PHP Package

1. Create `packages/php/your-package-name/`
2. Add `composer.json` with PSR-4 autoloading
3. Use the `example-package` scaffold as reference
4. Add scripts: `test`, `lint`, `format`, `analyse`

```json
{
  "name": "@monorepo/your-package-name",
  "autoload": {
    "psr-4": {
      "Monorepo\\YourPackage\\": "src/"
    }
  }
}
```

### JavaScript/TypeScript Package

1. Create `packages/js/your-package-name/`
2. Run `pnpm init` and configure as ESM module
3. Use the `example-package` scaffold as reference
4. Build with `tsup`, test with `vitest`

```json
{
  "name": "@monorepo/your-package-name",
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts"
}
```

### Python Package

1. Create `packages/python/your_package/`
2. Use Poetry: `poetry new --src packages/python/your-package`
3. Add to `pyproject.toml` under `[tool.poetry]`
4. Use ruff for linting/formatting, pytest for tests

```toml
[tool.poetry]
name = "your-package"
packages = [{ include = "your_package", from = "src" }]
```

### Go Package

1. Create `packages/go/your-package/`
2. Initialize: `go mod init github.com/monorepo/your-package`
3. Use the `example-package` scaffold as reference
4. Add `Makefile` with `test`, `lint`, `build` targets

### Rust Crate

1. Create `packages/rust/your-package/`
2. Initialize: `cargo new --lib packages/rust/your-package`
3. Use the `example-package` scaffold as reference
4. Add `[[bin]]` or `[lib]` section to `Cargo.toml`

## Development Setup

### Prerequisites

| Language | Version | Manager     |
| -------- | ------- | ----------- |
| PHP      | >= 8.1  | Composer    |
| Node.js  | >= 18   | pnpm        |
| Python   | >= 3.10 | Poetry / uv |
| Go       | >= 1.21 | go modules  |
| Rust     | >= 1.77 | Cargo       |

### Language-Specific Setup

```bash
# PHP
composer install

# JS/TS
pnpm install

# Python
poetry install
# or: uv sync

# Go
go mod download

# Rust
cargo fetch
```

## Package Scripts

| Command             | Description                        |
| ------------------- | ---------------------------------- |
| `pnpm build`        | Build all packages (via Turborepo) |
| `pnpm test`         | Test all packages                  |
| `pnpm lint`         | Lint all packages                  |
| `pnpm format`       | Format all packages                |
| `pnpm format:check` | Check formatting without changes   |
| `pnpm clean`        | Clean build artifacts              |

### Per-Package Commands

```bash
# PHP
cd packages/php/example-package
composer test
composer lint
composer format

# JS/TS
cd packages/js/example-package
pnpm test
pnpm lint
pnpm build

# Python
cd packages/python/example-package
poetry run pytest
poetry run ruff check .
poetry run mypy src/

# Go
cd packages/go/example-package
make test
make lint
make build

# Rust
cd packages/rust/example-package
cargo test
cargo clippy
cargo build
```

## Code Quality

All packages enforce consistent quality standards:

- **Formatting**: Prettier (JS), ruff (Python), gofmt (Go), rustfmt (Rust), PHP-CS-Fixer (PHP)
- **Linting**: ESLint (JS), ruff (Python), golangci-lint (Go), clippy (Rust), PHPStan + Psalm (PHP)
- **Type Checking**: TypeScript, mypy (Python), PHPStan (PHP)

Run all quality checks:

```bash
pnpm turbo run format:check lint typecheck
```

## Testing

Each package has its own test runner:

| Language | Test Runner | Command             |
| -------- | ----------- | ------------------- |
| PHP      | PHPUnit     | `composer test`     |
| JS/TS    | Vitest      | `pnpm test`         |
| Python   | pytest      | `poetry run pytest` |
| Go       | go test     | `go test ./...`     |
| Rust     | cargo test  | `cargo test`        |

Coverage reports are generated in `coverage/` directories.

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

feat(php): add new serializer class
fix(js): resolve memory leak in cache
chore: update dependencies
docs(python): add usage examples
```

### Types

| Type       | Description                     |
| ---------- | ------------------------------- |
| `feat`     | New feature                     |
| `fix`      | Bug fix                         |
| `perf`     | Performance improvement         |
| `refactor` | Code refactoring                |
| `test`     | Adding or updating tests        |
| `docs`     | Documentation changes           |
| `chore`    | Maintenance, dependency updates |
| `ci`       | CI configuration changes        |

## Release Process

Releases are automated via Changesets. See [RELEASING.md](./RELEASING.md) for details.

### Quick Release Flow

1. Make changes and commit with conventional messages
2. Run `pnpm changeset` to create a changeset
3. Open a PR — CI will validate all packages
4. Merge to `main` — Changesets bot opens a version PR
5. Merge the version PR — packages are published

## Questions?

Open an issue or reach out to the maintainers.
