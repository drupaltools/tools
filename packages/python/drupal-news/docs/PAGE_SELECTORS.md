# Page Selectors - Overview

## Overview

The Drupal News Aggregator allows you to configure custom CSS selectors for scraping web pages. This gives you precise control over which HTML elements to extract data from.

## Documentation Structure

This documentation has been split into focused topics for better readability and maintenance:

### Core Topics

- **[Page Selectors Basics](PAGE_SELECTORS_BASICS.md)** - Basic concepts, configuration formats, and CSS selector syntax
- **[Page Selectors Examples](PAGE_SELECTORS_EXAMPLES.md)** - Complete configuration examples for various web page structures
- **[Page Selectors How It Works](PAGE_SELECTORS_HOW_IT_WORKS.md)** - Technical details of the parsing flow and data extraction
- **[Page Selectors Testing](PAGE_SELECTORS_TESTING.md)** - Testing methods, troubleshooting, and debugging techniques
- **[Page Selectors Best Practices](PAGE_SELECTORS_BEST_PRACTICES.md)** - Best practices, advanced features, and maintenance guidelines

### Quick Start

For basic usage, start with the [Page Selectors Basics](PAGE_SELECTORS_BASICS.md) guide.

### Configuration Formats

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

## See Also

- [BeautifulSoup CSS Selector Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors)
- [MDN CSS Selectors Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- `config.example.json` - Example configuration file
