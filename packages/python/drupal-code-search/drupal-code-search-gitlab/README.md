# Drupal Code Search — GitLab

Search Drupal contributed modules on git.drupalcode.org using the GitLab API.

## Setup

1. Get a GitLab token from https://git.drupalcode.org/-/profile/personal_access_tokens
2. Add it to the shared `.env` file at the repository root:
   ```
   DRUPALORG_GITLAB_TOKEN=your_token_here
   ```

## Usage

```bash
python3 drupal_code_search_gitlab.py "WebformSubmissionInterface"
python3 drupal_code_search_gitlab.py "hook_form_alter" --limit 10
python3 drupal_code_search_gitlab.py "EntityTypeManager" --json
python3 drupal_code_search_gitlab.py "path:src/Plugin/Block/" --extension php
```

## Options

- `term` (positional): Search term
- `--limit`, `-n`: Number of results (default: 5)
- `--extension`, `-e`: Filter by file extension
- `--json`: Output as JSON
- `--no-branch`: Use commit hash instead of branch
- `--all`, `-a`: Show all results (up to 100)
