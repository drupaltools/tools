# Drupal Code Search — Sourcegraph

Search Drupal core on Sourcegraph.com using src-cli.

## Setup

1. Install src-cli: https://github.com/sourcegraph/src-cli
   ```bash
   brew install sourcegraph/src-cli/src-cli
   # or
   curl -L https://sourcegraph.com/.api/src-cli/src_linux_amd64 -o /usr/local/bin/src-cli
   chmod +x /usr/local/bin/src-cli
   ```
2. Add your token to the shared `.env` file at the repository root:
   ```
   SRC_ACCESS_TOKEN=your_token_here
   ```

## Usage

```bash
python3 drupal_code_search_sourcegraph.py "hook_form_alter"
python3 drupal_code_search_sourcegraph.py "EntityTypeManager" --version 10
python3 drupal_code_search_sourcegraph.py "implements TokenInterface" --json
python3 drupal_code_search_sourcegraph.py "class.*Block" -n 10 --stream
```

## Options

- `term` (positional): Search term or pattern
- `--version`, `-v`: Drupal branch: 7, 9, 10, 11, main (default: main)
- `--limit`, `-n`: Limit displayed results (streaming mode)
- `--json`: Output raw JSON from src-cli
- `--stream`: Stream results as they arrive
- `--dry-run`: Print the src-cli command without running
- `--endpoint`, `-e`: Sourcegraph endpoint (default: https://sourcegraph.com)
