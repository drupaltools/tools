//! Service for processing strings.

use crate::types::{ProcessOptions, ProcessResult};

/// Error types for the example package.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error {
    /// Input string was empty.
    EmptyInput,
}

impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::EmptyInput => write!(f, "input cannot be empty"),
        }
    }
}

impl std::error::Error for Error {}

fn default_transform(s: String) -> String {
    s.to_uppercase()
}

/// Service for processing strings with configurable transformations.
#[derive(Debug, Clone)]
pub struct ExampleService {
    prefix: Option<String>,
    suffix: Option<String>,
    transform: fn(String) -> String,
}

impl Default for ExampleService {
    fn default() -> Self {
        Self {
            prefix: None,
            suffix: None,
            transform: default_transform,
        }
    }
}

impl ExampleService {
    /// Creates a new [`ExampleService`] with default options.
    #[inline]
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Creates a new [`ExampleService`] with the given [`ProcessOptions`].
    #[inline]
    #[must_use]
    pub fn with_options(options: ProcessOptions) -> Self {
        Self {
            prefix: options.prefix,
            suffix: options.suffix,
            transform: options.transform.unwrap_or(default_transform),
        }
    }

    /// Sets the prefix.
    #[inline]
    #[must_use]
    pub fn prefix(mut self, prefix: impl Into<String>) -> Self {
        self.prefix = Some(prefix.into());
        self
    }

    /// Sets the suffix.
    #[inline]
    #[must_use]
    pub fn suffix(mut self, suffix: impl Into<String>) -> Self {
        self.suffix = Some(suffix.into());
        self
    }

    /// Sets a custom transform function.
    #[inline]
    #[must_use]
    pub fn transform(mut self, transform: fn(String) -> String) -> Self {
        self.transform = transform;
        self
    }

    /// Processes the input string.
    ///
    /// # Errors
    ///
    /// Returns [`Error::EmptyInput`] if `input` is empty or whitespace-only.
    pub fn process(&self, input: &str) -> Result<ProcessResult, Error> {
        let trimmed = input.trim();
        if trimmed.is_empty() {
            return Err(Error::EmptyInput);
        }

        let transformed = (self.transform)(trimmed.to_string());

        let mut value = transformed;
        if let Some(ref prefix) = self.prefix {
            value = format!("{prefix}{value}");
        }
        if let Some(ref suffix) = self.suffix {
            value = format!("{value}{suffix}");
        }

        Ok(ProcessResult::new(value, trimmed.to_string()))
    }

    /// Resets the service state.
    #[inline]
    pub fn reset(&mut self) {
        // No internal state to reset in current implementation
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_process_default_uppercase() {
        let service = ExampleService::new();
        let result = service.process("hello").unwrap();
        assert_eq!(result.value, "HELLO");
        assert_eq!(result.length, 5);
    }

    #[test]
    fn test_process_with_prefix() {
        let service = ExampleService::new().prefix(">>");
        let result = service.process("foo").unwrap();
        assert_eq!(result.value, ">>FOO");
    }

    #[test]
    fn test_process_with_suffix() {
        let service = ExampleService::new().suffix("<<");
        let result = service.process("bar").unwrap();
        assert_eq!(result.value, "BAR<<");
    }

    #[test]
    fn test_process_with_prefix_and_suffix() {
        let service = ExampleService::new().prefix(">>").suffix("<<");
        let result = service.process("baz").unwrap();
        assert_eq!(result.value, ">>BAZ<<");
    }

    #[test]
    fn test_process_custom_transform() {
        let service = ExampleService::new().transform(|s| s.to_lowercase());
        let result = service.process("HELLO").unwrap();
        assert_eq!(result.value, "hello");
    }

    #[test]
    fn test_process_empty_error() {
        let service = ExampleService::new();
        let result = service.process("");
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), Error::EmptyInput);
    }

    #[test]
    fn test_process_whitespace_error() {
        let service = ExampleService::new();
        let result = service.process("   ");
        assert!(result.is_err());
    }

    #[test]
    fn test_metadata_contains_original() {
        let service = ExampleService::new();
        let result = service.process("test").unwrap();
        assert_eq!(result.metadata.original, "test");
    }
}
