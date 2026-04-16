# Page Selectors - How It Works

This document explains the technical details of how the page selector system works in the Drupal News Aggregator.

## Parsing Flow

### Step 1: Fetch HTML

The aggregator downloads the HTML from the specified URL using HTTPX with proper headers and timeout settings.

```python
# Simplified fetch process
response = httpx.get(url, timeout=20, headers={"User-Agent": "DrupalNewsBot/1.0"})
html_content = response.text
```

### Step 2: Parse HTML with BeautifulSoup

The HTML is parsed using BeautifulSoup with the lxml parser for optimal performance.

```python
soup = BeautifulSoup(html_content, "lxml")
```

### Step 3: Find Containers

The system searches for all elements matching the `container` selector:

```python
containers = soup.select(selectors["container"])
```

### Step 4: Extract Data from Each Container

For each container element, the system extracts data using the configured selectors:

#### Extract Title
```python
title_element = container.select_one(selectors["title"])
if title_element:
    title = title_element.get_text().strip()
```

#### Extract Link
```python
# If link selector is specified
if "link" in selectors:
    link_element = container.select_one(selectors["link"])
else:
    # Fallback: find first <a> inside title element
    link_element = title_element.select_one("a") if title_element else None

if link_element and link_element.get("href"):
    link = link_element["href"]
```

#### Extract Description
```python
if "description" in selectors:
    desc_element = container.select_one(selectors["description"])
    if desc_element:
        description = desc_element.get_text().strip()
```

#### Extract Date
```python
if "date" in selectors:
    date_element = container.select_one(selectors["date"])
    if date_element:
        # Try datetime attribute first
        date_str = date_element.get("datetime") or date_element.get_text()
```

### Step 5: Normalize Data

#### Clean and Truncate Text
```python
# Clean text by removing extra whitespace
title = re.sub(r'\s+', ' ', title).strip()

# Truncate description if too long
if len(description) > 500:
    description = description[:497] + "..."
```

#### Convert Relative URLs to Absolute
```python
if link and link.startswith("/"):
    # Convert relative URL to absolute
    link = base_url + link
elif link and link.startswith("#"):
    # Skip anchor links
    link = None
```

#### Parse Dates
```python
# Try multiple date formats
date_formats = [
    "%Y-%m-%dT%H:%M:%S%z",  # ISO format
    "%Y-%m-%d %H:%M:%S",    # Standard format
    "%B %d, %Y",            # "October 30, 2025"
    "%d %B %Y",             # "30 October 2025"
]

for fmt in date_formats:
    try:
        parsed_date = datetime.strptime(date_str, fmt)
        break
    except ValueError:
        continue
```

#### Filter Items by Date Range
```python
# Only include items within the configured timeframe
if parsed_date and (since_date <= parsed_date <= until_date):
    items.append({
        "title": title,
        "link": link,
        "description": description,
        "date": parsed_date.isoformat()
    })
```

## Link Extraction Details

The aggregator is smart about extracting links:

### Link Extraction Logic

1. **If `link` selector points to an `<a>` tag**: Extract the `href` attribute
2. **If `link` selector points to another element**: Find the first `<a>` inside that element
3. **If no link selector provided**: Find the first `<a>` inside the title element
4. **If no link found**: Use the source URL as fallback

### URL Normalization

- **Relative URLs** (starting with `/`): Convert to absolute using `base_url`
- **Protocol-relative URLs** (starting with `//`): Add `https:` prefix
- **Anchor links** (starting with `#`): Skip (not valid external links)
- **JavaScript links** (`javascript:`, `#`): Skip

### Example: Link Extraction

```html
<!-- HTML structure -->
<article>
  <h2><a href="/news/2025/drupal-update">Drupal 11 Released</a></h2>
  <p>Exciting new features...</p>
  <time datetime="2025-10-30">October 30, 2025</time>
</article>
```

With selectors:
```json
{
  "container": "article",
  "title": "h2",
  "link": "h2 a"
}
```

**Result:**
- **Title**: "Drupal 11 Released"
- **Link**: "https://www.drupal.org/news/2025/drupal-update" (with base_url)

## Date Parsing Details

### Date Extraction Priority

1. **`datetime` attribute** (ISO format): `<time datetime="2025-10-30T14:30:00Z">`
2. **`data-*` attributes**: `<span data-date="2025-10-30">`
3. **Element text content**: `<span class="date">October 30, 2025</span>`

### Supported Date Formats

- **ISO 8601**: `2025-10-30T14:30:00Z`, `2025-10-30T14:30:00+00:00`
- **Common formats**: `2025-10-30`, `10/30/2025`, `30.10.2025`
- **Text formats**: `October 30, 2025`, `30 October 2025`, `Oct 30, 2025`
- **Relative formats**: `2 days ago`, `1 week ago` (limited support)

### Date Filtering

Items are filtered based on the configured timeframe:

```python
# Calculate date range
since_date = datetime.now(timezone.utc) - timedelta(days=timeframe_days)
until_date = datetime.now(timezone.utc)

# Filter items
if item_date and since_date <= item_date <= until_date:
    # Include item
else:
    # Exclude item (too old or future date)
```

## Error Handling

### Container Not Found

If no containers are found:
- Log warning message
- Return empty items list
- Continue processing other sources

### Selector Not Found

If a selector doesn't match any element:
- Use `None` for that field
- Continue processing other fields
- Log debug information

### Network Errors

If fetching the page fails:
- Retry up to configured retry count
- Log error with details
- Skip the source if all retries fail

## Performance Considerations

### Caching

- **HTML content** is cached to avoid repeated downloads
- **Parsed results** are cached for reuse
- **Cache TTL** is configurable (default: 21 days)

### Selector Optimization

- **Use specific selectors** for better performance
- **Avoid overly complex selectors** that require extensive DOM traversal
- **Use direct child selectors** (`>`) when possible

### Memory Management

- **Process pages sequentially** to avoid memory bloat
- **Clear parsed objects** after processing
- **Use streaming parsers** for large HTML documents

## Integration with Other Components

### RSS Reader Integration

Page selector results are combined with RSS feed results:

```python
# Combine all sources
all_items = rss_items + page_items

# Deduplicate based on URL and title
deduplicated_items = deduplicate(all_items)
```

### Validation

Extracted items are validated:
- **URL validation**: Check if URLs are accessible
- **Schema validation**: Ensure required fields are present
- **Content validation**: Check for minimum content quality

### Metrics Collection

Each page source is tracked with metrics:
- **Items found**: Number of containers matched
- **Items extracted**: Number of valid items after processing
- **Processing time**: Time taken to parse the page
- **Success rate**: Percentage of successful extractions

## See Also

- [Page Selectors Basics](PAGE_SELECTORS_BASICS.md) - Basic concepts and selector syntax
- [Page Selectors Examples](PAGE_SELECTORS_EXAMPLES.md) - Complete configuration examples
- [Page Selectors Testing](PAGE_SELECTORS_TESTING.md) - Testing and troubleshooting
- [Page Selectors Best Practices](PAGE_SELECTORS_BEST_PRACTICES.md) - Best practices and advanced features