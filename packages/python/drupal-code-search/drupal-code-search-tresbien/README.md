# Drupal Code Search — tresbien.tech

Search Drupal source code using the tresbien.tech code search engine.
No authentication required.

## Usage

```bash
python3 drupal_code_search_tresbien.py "hook_form_alter"
python3 drupal_code_search_tresbien.py "EntityTypeManager" --limit 5
python3 drupal_code_search_tresbien.py "implements TokenInterface" --lang php
python3 drupal_code_search_tresbien.py "hook_help" --context 3
python3 drupal_code_search_tresbien.py "class.*Block" --no-chunks --json
```

## Options

- `query` (positional): Search query (regex)
- `--limit`, `-n`: Number of file results (default: 10)
- `--context`, `-c`: Context lines around matches (default: 3)
- `--lang`, `-l`: Filter by language (php, yaml, twig)
- `--repo`, `-r`: Filter by repository name
- `--no-chunks`: Use LineMatches format instead of ChunkMatches
- `--json`: Output as JSON
- `--all-matches`, `-a`: Show all chunk matches per file
- `--stats`: Show search statistics
- `--maxmatches`: Stop after this many total matches
