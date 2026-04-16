"""JSON schema definitions for Drupal Aggregator."""

# Schema for a single news item
ITEM_SCHEMA = {
    "type": "object",
    "required": ["title", "url", "source_type"],
    "properties": {
        "title": {"type": "string", "minLength": 1},
        "url": {"type": "string", "format": "uri"},
        "description": {"type": "string"},
        "date": {"type": "string"},
        "source_type": {"type": "string", "enum": ["rss", "page"]},
        "source_url": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
    }
}

# Schema for sources.json
SOURCES_SCHEMA = {
    "type": "object",
    "required": ["items", "metadata"],
    "properties": {
        "items": {
            "type": "array",
            "items": ITEM_SCHEMA
        },
        "metadata": {
            "type": "object",
            "required": ["generated_at", "timeframe_days", "timezone"],
            "properties": {
                "generated_at": {"type": "string"},
                "timeframe_days": {"type": "integer"},
                "timezone": {"type": "string"},
                "total_items": {"type": "integer"},
            }
        }
    }
}

# Schema for validation_report.json
VALIDATION_SCHEMA = {
    "type": "object",
    "required": ["rss_count", "page_count", "passed"],
    "properties": {
        "rss_count": {"type": "integer"},
        "page_count": {"type": "integer"},
        "missing_links": {"type": "integer"},
        "invalid_urls": {"type": "integer"},
        "passed": {"type": "boolean"},
        "errors": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# Schema for metrics.json
METRICS_SCHEMA = {
    "type": "object",
    "required": ["timestamp", "provider", "model", "duration_s", "items_total", "exit_code"],
    "properties": {
        "timestamp": {"type": "string"},
        "provider": {"type": "string"},
        "model": {"type": "string"},
        "duration_s": {"type": "number"},
        "items_total": {"type": "integer"},
        "tokens_used": {"type": "integer"},
        "exit_code": {"type": "integer"},
        "cache_hits": {"type": "integer"},
        "cache_misses": {"type": "integer"},
        "errors": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}


def get_schema(schema_name: str) -> dict:
    """Get schema by name."""
    schemas = {
        "item": ITEM_SCHEMA,
        "sources": SOURCES_SCHEMA,
        "validation": VALIDATION_SCHEMA,
        "metrics": METRICS_SCHEMA,
    }
    return schemas.get(schema_name, {})
