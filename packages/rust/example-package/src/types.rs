//! Type definitions for the example package.

use std::time::{SystemTime, UNIX_EPOCH};

/// Options for configuring the [`ExampleService`](super::ExampleService).
#[derive(Debug, Clone, Default)]
pub struct ProcessOptions {
    /// Prefix to prepend to processed values.
    pub prefix: Option<String>,
    /// Suffix to append to processed values.
    pub suffix: Option<String>,
    /// Custom transform function. Defaults to uppercase.
    pub transform: Option<fn(String) -> String>,
}

impl ProcessOptions {
    /// Creates a new empty [`ProcessOptions`].
    #[inline]
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Sets the prefix.
    #[inline]
    #[must_use]
    pub fn with_prefix(mut self, prefix: impl Into<String>) -> Self {
        self.prefix = Some(prefix.into());
        self
    }

    /// Sets the suffix.
    #[inline]
    #[must_use]
    pub fn with_suffix(mut self, suffix: impl Into<String>) -> Self {
        self.suffix = Some(suffix.into());
        self
    }

    /// Sets a custom transform function.
    #[inline]
    #[must_use]
    pub fn with_transform(mut self, transform: fn(String) -> String) -> Self {
        self.transform = Some(transform);
        self
    }
}

/// Metadata about a processed input.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProcessMetadata {
    /// The original input string.
    pub original: String,
    /// Unix timestamp when processing occurred.
    pub processed_at: u64,
}

impl ProcessMetadata {
    /// Creates new metadata from the original input.
    pub(crate) fn new(original: String) -> Self {
        let processed_at = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0);
        Self {
            original,
            processed_at,
        }
    }
}

/// Result of processing an input string.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProcessResult {
    /// The processed string value.
    pub value: String,
    /// Length of the processed value.
    pub length: usize,
    /// Processing metadata.
    pub metadata: ProcessMetadata,
}

impl ProcessResult {
    /// Creates a new result.
    pub(crate) fn new(value: String, original: String) -> Self {
        let length = value.len();
        Self {
            value,
            length,
            metadata: ProcessMetadata::new(original),
        }
    }
}
