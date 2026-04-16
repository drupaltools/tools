//! Example package from the polyglot monorepo.
//!
//! # Example
//!
//! ```
//! use example_package::{ExampleService, ProcessOptions};
//!
//! let service = ExampleService::new();
//! let result = service.process("hello").unwrap();
//! assert_eq!(result.value, "HELLO");
//! ```

pub mod service;
pub mod types;

pub use service::ExampleService;
pub use types::{ProcessMetadata, ProcessOptions, ProcessResult};
