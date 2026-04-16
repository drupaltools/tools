# Page Selectors - Testing and Troubleshooting

This document covers testing methods and troubleshooting for page selector configurations.

## Testing Selectors

### Browser Developer Tools

The easiest way to test selectors is using browser developer tools:

#### Chrome/Firefox Developer Tools

1. **Open the target page** in Chrome or Firefox
2. **Press F12** to open Developer Tools
3. **Use "Select Element" tool** (Ctrl+Shift+C or Cmd+Shift+C)
4. **Click on the element** you want to select
5. **Right-click the element** in the Elements panel → Copy → Copy selector

#### Testing Selectors in Console

```javascript
// Test container selector
console.log(document.querySelectorAll("article").length);

// Test title selector on first container
const container = document.querySelector("article");
if (container) {
  console.log(container.querySelector("h2")?.textContent);
}
```

#### Browser Extensions

- **SelectorGadget** - Interactive CSS selector generator
- **XPath Helper** - For XPath selectors (can be converted to CSS)
- **Web Scraper** - Browser extension for testing selectors

### Testing with Python

You can test selectors directly with Python using BeautifulSoup:

#### Basic Testing Script

```python
from bs4 import BeautifulSoup
import httpx

# Fetch page
url = "https://www.drupal.org/news"
response = httpx.get(url)
soup = BeautifulSoup(response.text, "lxml")

# Test container selector
containers = soup.select("article")
print(f"Found {len(containers)} containers")

# Test title selector on first container
if containers:
    title = containers[0].select_one("h2")
    print(f"Title: {title.get_text() if title else 'Not found'}")

    # Test link selector
    link = containers[0].select_one("h2 a")
    print(f"Link: {link.get('href') if link else 'Not found'}")

    # Test description selector
    description = containers[0].select_one(".field--name-body")
    print(f"Description: {description.get_text()[:100] if description else 'Not found'}")

    # Test date selector
    date = containers[0].select_one("time")
    print(f"Date: {date.get('datetime') if date else 'Not found'}")
```

#### Advanced Testing Function

```python
def test_selectors(url, selectors):
    """Test selectors on a given URL"""
    try:
        response = httpx.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        results = {
            "url": url,
            "containers_found": 0,
            "items": []
        }

        containers = soup.select(selectors["container"])
        results["containers_found"] = len(containers)

        for i, container in enumerate(containers[:3]):  # Test first 3
            item = {"container": i + 1}

            # Test title
            title_elem = container.select_one(selectors["title"])
            item["title"] = title_elem.get_text().strip() if title_elem else None

            # Test link
            link_elem = container.select_one(selectors.get("link", selectors["title"] + " a"))
            item["link"] = link_elem.get("href") if link_elem else None

            # Test description
            if "description" in selectors:
                desc_elem = container.select_one(selectors["description"])
                item["description"] = desc_elem.get_text().strip() if desc_elem else None

            # Test date
            if "date" in selectors:
                date_elem = container.select_one(selectors["date"])
                item["date"] = date_elem.get("datetime") or (date_elem.get_text().strip() if date_elem else None)

            results["items"].append(item)

        return results

    except Exception as e:
        return {"error": str(e)}

# Usage
test_results = test_selectors(
    "https://www.drupal.org/news",
    {
        "container": "article",
        "title": "h2",
        "link": "h2 a",
        "description": ".field--name-body",
        "date": "time"
    }
)
print(test_results)
```

## Troubleshooting

### No Items Found

**Problem**: Aggregator returns 0 items for a page

**Solutions**:

1. **Verify `container` selector** matches elements on the page
   ```python
   # Test in browser console
   document.querySelectorAll("article").length
   ```

2. **Check for dynamic content** (JavaScript-loaded)
   - Some pages load content after initial page load
   - Check browser "Network" tab for AJAX requests
   - Consider using headless browser tools like Playwright

3. **Try broader selectors**
   ```json
   "container": "article"  // Instead of "article.specific-class"
   ```

4. **Check for iframes**
   - Content might be in an `<iframe>`
   - You'll need to target the iframe source URL

### Wrong Content Extracted

**Problem**: Extracted content doesn't match expected data

**Solutions**:

1. **Use more specific selectors** with classes/IDs
   ```json
   "title": "h2.article-title"  // Instead of "h2"
   ```

2. **Use descendant selectors** for precise targeting
   ```json
   "title": "article > h2"  // Direct child instead of descendant
   ```

3. **Check HTML structure** in browser developer tools
   - Verify the actual HTML structure
   - Look for nested elements

4. **Use attribute selectors** for precise matching
   ```json
   "container": "article[data-type='news']"
   ```

### Relative Links Not Working

**Problem**: Links are broken or point to wrong URLs

**Solutions**:

1. **Set correct `base_url`** for the domain
   ```json
   "base_url": "https://www.drupal.org"
   ```

2. **Check link formats**
   - `/path` - relative (needs base_url)
   - `//example.com/path` - protocol-relative
   - `https://example.com/path` - absolute

3. **Verify link extraction**
   ```python
   # Test link extraction
   link_elem = container.select_one("h2 a")
   print(f"Raw href: {link_elem.get('href')}")
   ```

### Date Filtering Not Working

**Problem**: Items outside date range are included

**Solutions**:

1. **Verify `date` selector** points to element with date info
2. **Check for `datetime` attribute**
   ```html
   <time datetime="2025-10-30">October 30, 2025</time>
   ```

3. **Date parsing may fail** on non-standard formats
   - Check the actual date format in the HTML
   - Consider using multiple date selectors

4. **Test date extraction**
   ```python
   date_elem = container.select_one("time")
   print(f"Date text: {date_elem.get_text()}")
   print(f"Date attribute: {date_elem.get('datetime')}")
   ```

### Performance Issues

**Problem**: Page parsing is slow or times out

**Solutions**:

1. **Use more specific selectors**
   - Avoid `*` (universal selector)
   - Use IDs when possible

2. **Limit the number of containers**
   ```json
   "container": "article:lt(50)"  // First 50 articles (if supported)
   ```

3. **Check network conditions**
   - Slow server response
   - Large HTML files

4. **Enable caching** to avoid repeated downloads

## Common Issues and Solutions

### Dynamic Content

**Issue**: Content loaded via JavaScript after page load

**Solutions**:
- Use headless browser automation (Playwright, Selenium)
- Check for API endpoints that serve the data directly
- Look for JSON-LD or microdata in the page source

### Pagination

**Issue**: Only first page of content is scraped

**Solutions**:
- Configure multiple URLs for different pages
- Look for pagination patterns in URLs
- Use the aggregator's scheduler for regular updates

### Authentication

**Issue**: Page requires login or has access restrictions

**Solutions**:
- Use authenticated sessions (cookies, tokens)
- Consider using public RSS feeds instead
- Contact site owner for API access

### Rate Limiting

**Issue**: Site blocks requests due to rate limiting

**Solutions**:
- Implement delays between requests
- Use caching to minimize requests
- Respect robots.txt and rate limits

## Testing Checklist

Before deploying a new page selector configuration:

- [ ] **Container selector** matches expected number of items
- [ ] **Title selector** extracts correct text
- [ ] **Link selector** extracts valid URLs
- [ ] **Description selector** extracts meaningful content
- [ ] **Date selector** extracts parseable dates
- [ ] **Relative URLs** are converted correctly
- [ ] **Date filtering** works as expected
- [ ] **Performance** is acceptable
- [ ] **Error handling** works for edge cases

## Debugging Tools

### Log Analysis

Check the aggregator logs for detailed information:

```bash
# Check the latest run log
tail -f runs/$(date +%Y-%m-%d)/run.log

# Search for page selector related logs
grep "page\|selector" runs/$(date +%Y-%m-%d)/run.log
```

### Metrics Analysis

Review metrics for performance and success rates:

```bash
# Check page source metrics
cat runs/$(date +%Y-%m-%d)/metrics.json | jq '.sources.pages'
```

### Manual Testing

Use the aggregator's test mode:

```bash
# Test specific page source
./index.py --fetch-only --verbose

# Check parsed results
cat runs/$(date +%Y-%m-%d)/parsed.md | head -20
```

## See Also

- [Page Selectors Basics](PAGE_SELECTORS_BASICS.md) - Basic concepts and selector syntax
- [Page Selectors Examples](PAGE_SELECTORS_EXAMPLES.md) - Complete configuration examples
- [Page Selectors How It Works](PAGE_SELECTORS_HOW_IT_WORKS.md) - Technical details and parsing flow
- [Page Selectors Best Practices](PAGE_SELECTORS_BEST_PRACTICES.md) - Best practices and advanced features