"""Cache manager for Drupal Newsletter using SQLite."""
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import hashlib


class CacheManager:
    """Manages persistent caching with SQLite."""

    def __init__(self, db_path: str = "./cache/cache.db", ttl_days: int = 21):
        """
        Initialize cache manager.

        Args:
            db_path: Path to SQLite database
            ttl_days: Time-to-live for cache entries in days
        """
        self.db_path = Path(db_path)
        self.ttl_days = ttl_days
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
        """)

        conn.commit()
        conn.close()

    def _compute_key(self, url: str) -> str:
        """Compute cache key from URL."""
        return hashlib.sha256(url.encode()).hexdigest()

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached value for URL.

        Returns:
            Cached value if found and not expired, None otherwise
        """
        key = self._compute_key(url)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT value, expires_at FROM cache WHERE key = ?
        """, (key,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        value_json, expires_at = row
        expires_dt = datetime.fromisoformat(expires_at)

        # Check expiration
        if datetime.now() > expires_dt:
            self.delete(url)
            return None

        try:
            return json.loads(value_json)
        except json.JSONDecodeError:
            return None

    def set(self, url: str, value: Dict[str, Any]):
        """
        Set cached value for URL.

        Args:
            url: URL to cache
            value: Dictionary value to cache
        """
        key = self._compute_key(url)
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(days=self.ttl_days)).isoformat()

        value_json = json.dumps(value, ensure_ascii=False)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO cache (key, value, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (key, value_json, created_at, expires_at))

        conn.commit()
        conn.close()

    def delete(self, url: str):
        """Delete cached value for URL."""
        key = self._compute_key(url)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cache WHERE key = ?", (key,))

        conn.commit()
        conn.close()

    def purge_expired(self) -> int:
        """
        Remove all expired cache entries.

        Returns:
            Number of entries removed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("DELETE FROM cache WHERE expires_at < ?", (now,))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count

    def clear_all(self):
        """Clear all cache entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM cache")

        conn.commit()
        conn.close()

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with total, expired, and valid counts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM cache")
        total = cursor.fetchone()[0]

        now = datetime.now().isoformat()
        cursor.execute("SELECT COUNT(*) FROM cache WHERE expires_at < ?", (now,))
        expired = cursor.fetchone()[0]

        conn.close()

        return {
            "total": total,
            "expired": expired,
            "valid": total - expired
        }
