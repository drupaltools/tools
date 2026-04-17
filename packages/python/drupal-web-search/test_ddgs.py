from pathlib import Path
from drupal_web_search.config import load_config
from drupal_web_search.search import _search_ddgs

config = load_config(Path("config.toml"))
print("config.search.timeout:", config.search.timeout)

query = "site:drupal.org site:api.drupal.org site:git.drupalcode.org site:drupal.stackexchange.com drupal"

print("Calling _search_ddgs...")
results = _search_ddgs(query, 2, config)
print("Results:", results)
print("Count:", len(results))
