# Page Selectors - Examples and Configurations

This document provides complete configuration examples for various web page structures.

## Complete Examples

### Example 1: Drupal News Page

```json
{
  "url": "https://www.drupal.org/news",
  "name": "Drupal Official News",
  "base_url": "https://www.drupal.org",
  "selectors": {
    "container": "article.node--type-blog-post",
    "title": "h2.node__title",
    "link": "h2.node__title a",
    "description": ".field--name-body",
    "date": "time"
  }
}
```

**Structure Analysis:**
- **Container**: `<article>` elements with class `node--type-blog-post`
- **Title**: `<h2>` elements with class `node__title`
- **Link**: `<a>` tags inside the title `<h2>`
- **Description**: Elements with class `field--name-body`
- **Date**: `<time>` elements (uses `datetime` attribute)

### Example 2: Custom Blog with Specific Structure

```json
{
  "url": "https://example.com/drupal-updates",
  "name": "Example Drupal Blog",
  "base_url": "https://example.com",
  "selectors": {
    "container": "#blog-posts .post-item",
    "title": ".post-title h3",
    "link": ".post-title a",
    "description": ".post-excerpt",
    "date": ".post-meta time"
  }
}
```

**Structure Analysis:**
- **Container**: Elements with class `post-item` inside element with ID `blog-posts`
- **Title**: `<h3>` elements inside elements with class `post-title`
- **Link**: `<a>` tags inside the title container
- **Description**: Elements with class `post-excerpt`
- **Date**: `<time>` elements inside elements with class `post-meta`

### Example 3: Complex Nested Structure

```json
{
  "url": "https://www.drupal.org/planet",
  "name": "Drupal Planet",
  "selectors": {
    "container": "div.view-content > article",
    "title": "h2 a",
    "link": "h2 a",
    "description": "div.content p:first-of-type",
    "date": "footer time[datetime]"
  }
}
```

**Structure Analysis:**
- **Container**: `<article>` elements that are direct children of `<div class="view-content">`
- **Title**: `<a>` tags inside `<h2>` elements
- **Link**: Same as title (link is extracted from the `<a>` tag)
- **Description**: First `<p>` element inside `<div class="content">`
- **Date**: `<time>` elements with `datetime` attribute inside `<footer>`

### Example 4: Using Data Attributes

```json
{
  "url": "https://events.drupal.org/",
  "name": "Drupal Events",
  "selectors": {
    "container": "article[data-type='event']",
    "title": ".event-title",
    "link": ".event-title a",
    "description": ".event-description",
    "date": "time[data-start-date]"
  }
}
```

**Structure Analysis:**
- **Container**: `<article>` elements with `data-type="event"` attribute
- **Title**: Elements with class `event-title`
- **Link**: `<a>` tags inside the title container
- **Description**: Elements with class `event-description`
- **Date**: `<time>` elements with `data-start-date` attribute

### Example 5: Simple Blog Structure

```json
{
  "url": "https://blog.example.com/drupal",
  "name": "Drupal Blog",
  "base_url": "https://blog.example.com",
  "selectors": {
    "container": "article",
    "title": "h1",
    "link": "h1 a",
    "description": ".entry-content",
    "date": ".entry-date"
  }
}
```

### Example 6: News Portal with Multiple Sections

```json
{
  "url": "https://news.example.com/technology/drupal",
  "name": "Tech News Drupal Section",
  "base_url": "https://news.example.com",
  "selectors": {
    "container": ".news-list .item",
    "title": ".title a",
    "link": ".title a",
    "description": ".summary",
    "date": ".meta .date"
  }
}
```

### Example 7: Forum or Discussion Board

```json
{
  "url": "https://forum.example.com/drupal",
  "name": "Drupal Forum",
  "base_url": "https://forum.example.com",
  "selectors": {
    "container": ".topic",
    "title": ".topic-title a",
    "link": ".topic-title a",
    "description": ".topic-excerpt",
    "date": ".topic-meta .date"
  }
}
```

## Configuration Templates

### Template for Standard Blog

```json
{
  "url": "https://example.com/blog",
  "name": "Blog Name",
  "base_url": "https://example.com",
  "selectors": {
    "container": "article",
    "title": "h2, h1",
    "link": "h2 a, h1 a",
    "description": ".entry-content, .post-content, .summary",
    "date": "time, .date, .published"
  }
}
```

### Template for News Portal

```json
{
  "url": "https://news.example.com/section",
  "name": "News Portal Section",
  "base_url": "https://news.example.com",
  "selectors": {
    "container": ".news-item, article",
    "title": ".title a, h3 a",
    "link": ".title a, h3 a",
    "description": ".summary, .excerpt, p:first-of-type",
    "date": "time, .date, .meta"
  }
}
```

### Template for Custom CMS

```json
{
  "url": "https://cms.example.com/content",
  "name": "Custom CMS Content",
  "base_url": "https://cms.example.com",
  "selectors": {
    "container": "[data-content-type='article']",
    "title": ".content-title",
    "link": ".content-title a",
    "description": ".content-body p:first-of-type",
    "date": "[data-published-date]"
  }
}
```

## Migration Examples

### From Simple URL to Selector Configuration

**Before (simple URL):**
```json
"pages": [
  "https://www.drupal.org/news"
]
```

**After (selector configuration):**
```json
"pages": [
  {
    "url": "https://www.drupal.org/news",
    "name": "Drupal Official News",
    "base_url": "https://www.drupal.org",
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

## Common Patterns

### WordPress Sites

```json
{
  "url": "https://wordpress-site.com/category/drupal",
  "name": "WordPress Drupal Category",
  "base_url": "https://wordpress-site.com",
  "selectors": {
    "container": "article.post",
    "title": "h2.entry-title a",
    "link": "h2.entry-title a",
    "description": ".entry-summary",
    "date": "time.entry-date"
  }
}
```

### Joomla Sites

```json
{
  "url": "https://joomla-site.com/drupal",
  "name": "Joomla Drupal Section",
  "base_url": "https://joomla-site.com",
  "selectors": {
    "container": ".item-page",
    "title": ".page-header h2 a",
    "link": ".page-header h2 a",
    "description": ".article-intro",
    "date": ".createdate"
  }
}
```

### Custom Framework Sites

```json
{
  "url": "https://framework-site.com/news",
  "name": "Custom Framework News",
  "base_url": "https://framework-site.com",
  "selectors": {
    "container": "[data-news-item]",
    "title": "[data-news-title] a",
    "link": "[data-news-title] a",
    "description": "[data-news-summary]",
    "date": "[data-news-date]"
  }
}
```

## See Also

- [Page Selectors Basics](PAGE_SELECTORS_BASICS.md) - Basic concepts and selector syntax
- [Page Selectors How It Works](PAGE_SELECTORS_HOW_IT_WORKS.md) - Technical details and parsing flow
- [Page Selectors Testing](PAGE_SELECTORS_TESTING.md) - Testing and troubleshooting
- [Page Selectors Best Practices](PAGE_SELECTORS_BEST_PRACTICES.md) - Best practices and advanced features