# Page Selectors - Best Practices and Advanced Features

## Best Practices

### Selector Design

#### Use Specific Selectors

```json
// Good - specific
"title": "h2.article-title"

// Avoid - too generic
"title": "h2"
```

#### Prefer Direct Child Selectors

```json
// Good - direct child
"title": "article > h2"

// Avoid - descendant (slower)
"title": "article h2"
```

#### Use Attribute Selectors for Precision

```json
// Good - specific attribute
"container": "article[data-type='news']"
"date": "time[datetime]"

// Avoid - generic
"container": "article"
```

### Configuration Organization

#### Use Meaningful Names

```json
{
  "url": "https://www.drupal.org/news",
  "name": "Drupal Official News", // Clear, descriptive
  "base_url": "https://www.drupal.org",
  "selectors": {
    /* ... */
  }
}
```

#### Group Related Sources

```json
"pages": [
  {
    "url": "https://www.drupal.org/news",
    "name": "Drupal Core News",
    "selectors": { /* ... */ }
  },
  {
    "url": "https://www.drupal.org/planet",
    "name": "Drupal Community",
    "selectors": { /* ... */ }
  }
]
```

### Performance Optimization

#### Limit Container Count

```json
// For performance, limit to reasonable number
"container": "article:lt(50)"  // First 50 articles
```

#### Use Efficient Selectors

```json
// Good - ID selector (fastest)
"container": "#main-content article"

// Good - class selector
"container": ".news-item"

// Avoid - complex selectors
"container": "div.content section:first-child article:not(.archived)"
```

#### Cache Configuration

```json
// Enable caching for stable pages
"cache_ttl": 3600  // 1 hour cache
```

### Error Handling

#### Graceful Degradation

```python
# Handle missing elements gracefully
title = container.select_one(selectors["title"])
if title:
    title_text = title.get_text().strip()
else:
    title_text = None  # Continue without title
```

#### Multiple Selector Options

```json
// Provide fallback selectors
"title": "h2.article-title, h2, h1"
"date": "time[datetime], .date, .published"
```

## Advanced Features

### Conditional Selectors

#### Dynamic Content Handling

```json
// Handle different page layouts
"selectors": {
  "container": "article, .news-item, [data-content-type='article']",
  "title": "h2, h1, .title"
}
```

#### JavaScript-Rendered Content

For pages with JavaScript-loaded content:

- Use headless browser automation (Playwright, Selenium)
- Check for API endpoints that serve data directly
- Look for JSON-LD or microdata in page source

### Multi-Page Scraping

#### Pagination Support

```json
// Configure multiple pages for paginated content
"pages": [
  {
    "url": "https://example.com/news?page=1",
    "name": "News Page 1",
    "selectors": { /* ... */ }
  },
  {
    "url": "https://example.com/news?page=2",
    "name": "News Page 2",
    "selectors": { /* ... */ }
  }
]
```

#### URL Pattern Matching

```json
// Use URL patterns for dynamic pagination
"url_pattern": "https://example.com/news?page={}",
"pages": [1, 2, 3, 4, 5]
```

### Data Transformation

#### Custom Text Processing

```python
# Example: Clean extracted text
def clean_text(text):
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove common prefixes
    text = re.sub(r'^\s*[\-\*•]\s*', '', text)
    return text
```

#### Date Format Normalization

```python
# Handle multiple date formats
date_formats = [
    "%Y-%m-%dT%H:%M:%S%z",  # ISO format
    "%Y-%m-%d %H:%M:%S",    # Standard format
    "%B %d, %Y",            # "October 30, 2025"
    "%d %B %Y",             # "30 October 2025"
]
```

### Validation and Testing

#### Selector Validation

```python
def validate_selectors(url, selectors):
    """Validate selectors before deployment"""
    try:
        response = httpx.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        # Test container selector
        containers = soup.select(selectors["container"])
        if not containers:
            return {"error": "No containers found"}

        # Test other selectors on first container
        container = containers[0]
        for field, selector in selectors.items():
            if field != "container":
                element = container.select_one(selector)
                if not element:
                    return {"warning": f"Selector '{field}' not found"}

        return {"success": "All selectors validated"}

    except Exception as e:
        return {"error": str(e)}
```

#### Performance Monitoring

```python
# Track selector performance
import time

start_time = time.time()
containers = soup.select(selectors["container"])
processing_time = time.time() - start_time

if processing_time > 5.0:  # 5 seconds threshold
    logger.warning(f"Slow selector: {selectors['container']} took {processing_time:.2f}s")
```

## Security Considerations

### Rate Limiting

```json
// Respect site rate limits
"rate_limit": {
  "requests_per_minute": 60,
  "delay_between_requests": 1.0
}
```

### User Agent Configuration

```json
// Use descriptive user agent
"http": {
  "user_agent": "DrupalNewsBot/1.0 (+https://github.com/drupaltools/tools)"
}
```

### Robots.txt Compliance

```python
# Check robots.txt before scraping
import urllib.robotparser

rp = urllib.robotparser.RobotFileParser()
rp.set_url(f"{base_url}/robots.txt")
rp.read()

if not rp.can_fetch("DrupalNewsBot", url):
    logger.warning(f"Blocked by robots.txt: {url}")
    return []
```

## Maintenance

### Regular Testing

- Test selectors after site updates
- Monitor for selector breakage
- Keep backup configurations

### Version Control

- Store selector configurations in version control
- Track changes to site structures
- Maintain change history

### Documentation

- Document selector choices and reasoning
- Include troubleshooting notes
- Update when site structure changes

## See Also

- [Page Selectors Basics](PAGE_SELECTORS_BASICS.md) - Basic concepts and selector syntax
- [Page Selectors Examples](PAGE_SELECTORS_EXAMPLES.md) - Complete configuration examples
- [Page Selectors How It Works](PAGE_SELECTORS_HOW_IT_WORKS.md) - Technical details and parsing flow
- [Page Selectors Testing](PAGE_SELECTORS_TESTING.md) - Testing and troubleshooting
