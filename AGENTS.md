# Monorepo — OpenCode Agent Guide

## Repository Identity

- **URL**: `https://github.com/drupaltools/tools`
- **Team**: `DrupalTools`
- **Email**: `drupaltools@tplcom.mozmail.com`

## Repository Structure

```
monorepo/
├── packages/
│   ├── php/        # Composer/PSR-4 packages
│   ├── js/         # npm/TypeScript packages
│   ├── python/     # setuptools packages
│   ├── go/         # Go modules
│   └── rust/       # Cargo crates
├── .github/workflows/
│   ├── ci.yml      # Unified CI pipeline
│   └── release.yml  # Changeset-driven publishing
├── .changeset/     # Independent per-package versioning
└── [config files]  # turbo.json, pnpm-workspace.yaml, prettier, eslint, commitlint, ruff
```

## Developer Commands

```bash
# Monorepo-wide (run from root)
pnpm install              # Install all workspace dependencies
pnpm turbo run build     # Build all packages
pnpm turbo run test      # Test all packages
pnpm turbo run lint      # Lint all packages
pnpm turbo run format    # Format all packages
pnpm turbo run clean     # Clean build artifacts
pnpm changeset           # Create a changeset (run before PR to main)
pnpm exec husky install  # Activate pre-commit hooks

# Single package
pnpm turbo run test --filter=@scope/package-name
pnpm turbo run lint --filter=@scope/package-name
```

## Per-Language Tooling

| Language | Lint           | Format       | Type check  | Test       |
| -------- | -------------- | ------------ | ----------- | ---------- |
| PHP      | PHPStan, Psalm | PHP-CS-Fixer | PHPStan     | PHPUnit    |
| JS/TS    | ESLint         | Prettier     | TypeScript  | Vitest     |
| Python   | ruff           | ruff format  | mypy        | pytest     |
| Go       | golangci-lint  | gofmt        | go vet      | go test    |
| Rust     | clippy         | cargo fmt    | cargo check | cargo test |

### Per-package commands

```bash
# PHP
composer install && composer test && composer lint && composer format

# JS/TS
pnpm install && pnpm test && pnpm lint && pnpm build

# Python — check the package's pyproject.toml for its specific scripts and dependencies

# Go
go mod download && make test && make lint && make build

# Rust
cargo test && cargo clippy && cargo fmt && cargo build
```

## Conventions

### Commit messages — Conventional Commits

Format: `<type>(<scope>): <description>`

Examples: `feat(python): add new feature`, `fix(php): resolve bug`, `chore: update deps`

Types: `feat`, `fix`, `perf`, `refactor`, `style`, `test`, `build`, `ci`, `chore`, `docs`, `revert`

Scopes: `php`, `js`, `python`, `go`, `rust`, `ci`, `docs`

Pre-commit hooks enforce this via commitlint.

### Package versioning — Changesets

- Each package has independent semver
- Before merging to `main`: run `pnpm changeset` to create a `.changeset/` file
- Merging to `main` opens an automatic version PR
- Merging the version PR publishes to registries

### File and directory naming

| Language | Convention           | Example                        |
| -------- | -------------------- | ------------------------------ |
| Python   | Underscores          | `my_module.py`, `my_package/`  |
| Ruby     | Underscores          | `my_script.rb`                 |
| Bash     | Underscores          | `build.sh`, `setup.sh`         |
| JS/TS    | kebab-case for files | `my-component.tsx`, `build.sh` |

Python module imports require underscores — `import my-package` is invalid (hyphen is parsed as minus).

## Root Toolchain

- **pnpm@9** enforced via `packageManager` in root `package.json`
- Node ≥18 required
- Turborepo remote cache: set `TURBO_TOKEN` + `TURBO_TEAM` secrets

## Adding a New Package

1. Create under `packages/<lang>/your-package/`
2. Add to `pnpm-workspace.yaml` if not covered by `packages/*`
3. Add Turborepo task overrides to `turbo.json` if non-standard script names
4. Add CI job to `.github/workflows/ci.yml`
5. Run `pnpm changeset` to register for versioning

## Reference Files

- `CONTRIBUTING.md` — full per-language setup guide
- `RELEASING.md` — Changesets workflow detail
