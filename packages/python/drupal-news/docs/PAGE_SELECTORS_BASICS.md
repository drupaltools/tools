# Page Selectors - Basic Concepts and Syntax

## Overview

The Drupal News Aggregator allows you to configure custom CSS selectors for scraping web pages. This gives you precise control over which HTML elements to extract data from.

## Basic Concepts

### Two Configuration Formats

The `sources.pages` array in `config.json` supports two formats:

1. **Simple URL String** (backward compatible)
   ```json
   "pages": [
     "https://www.drupal.org/news"
   ]
   ```

2. **Object with Selectors** (advanced control)
   ```json
   "pages": [
     {
       "url": "https://www.drupal.org/news",
       "selectors": {
         "container": "article",
         "title": "h2",
         "link": "h2 a",
         "description": ".field--name-body",
         "date": "time"
       }
     }
   ]
   ```

## Selector Configuration

### Required Fields

- **`url`** - The page URL to scrape
- **`selectors.container`** - CSS selector for the container element that wraps each item
- **`selectors.title`** - CSS selector for the title element

### Optional Fields

- **`name`** - Human-readable name for this source (for logging)
- **`base_url`** - Base URL for converting relative links to absolute (default: `https://www.drupal.org`)
- **`selectors.link`** - CSS selector for the link element (defaults to `title` selector if not provided)
- **`selectors.description`** - CSS selector for the description/content element
- **`selectors.date`** - CSS selector for the date element

## CSS Selector Syntax

All selectors use standard CSS selector syntax supported by BeautifulSoup's `select()` and `select_one()` methods.

### Common Selector Patterns

#### Tag Selectors
```json
"container": "article"        // All <article> elements
"title": "h2"                 // All <h2> elements
"date": "time"                // All <time> elements
```

#### Class Selectors
```json
"container": ".news-item"     // Elements with class="news-item"
"title": ".article-title"     // Elements with class="article-title"
"description": ".summary"     // Elements with class="summary"
```

#### ID Selectors
```json
"container": "#main-content"  // Element with id="main-content"
```

#### Descendant Selectors
```json
"container": "div.content article"     // <article> inside <div class="content">
"title": "article h2"                  // <h2> inside <article>
"link": "h2 a"                         // <a> inside <h2>
```

#### Direct Child Selector
```json
"container": "div > article"           // <article> that is direct child of <div>
"description": "article > .body"       // .body that is direct child of <article>
```

#### Attribute Selectors
```json
"container": "article[data-type='news']"  // <article> with data-type="news"
"date": "time[datetime]"                  // <time> with datetime attribute
```

#### Pseudo-selectors
```json
"description": "article p:first-of-type"  // First <p> in <article>
"link": "article a:not(.external)"        // <a> without class="external"
```

#### Multiple Selectors (OR)
```json
"title": "h2, h3"                      // <h2> OR <h3>
"date": "time, .date, span.published"  // Multiple options
```

## See Also

- [Page Selectors Examples](PAGE_SELECTORS_EXAMPLES.md) - Complete configuration examples
- [Page Selectors How It Works](PAGE_SELECTORS_HOW_IT_WORKS.md) - Technical details and parsing flow
- [Page Selectors Testing](PAGE_SELECTORS_TESTING.md) - Testing and troubleshooting
- [Page Selectors Best Practices](PAGE_SELECTORS_BEST_PRACTICES.md) - Best practices and advanced features