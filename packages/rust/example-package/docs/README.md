# example-package Documentation

See the [main README](../README.md) for usage instructions.

## Architecture

- `src/lib.rs` — Public API and module re-exports
- `src/types.rs` — Core data types (`ProcessOptions`, `ProcessResult`, `ProcessMetadata`)
- `src/service.rs` — `ExampleService` implementation with configurable string transforms
