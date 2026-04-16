# example-package

Example Rust crate from the polyglot monorepo.

## Installation

Add to `Cargo.toml`:

```toml
[dependencies]
example-package = "0.1.0"
```

## Usage

```rust
use example_package::{ExampleService, ProcessOptions};

let service = ExampleService::new()
    .prefix(">>")
    .suffix("<<");

let result = service.process("hello").unwrap();
assert_eq!(result.value, ">>HELLO<<");
```

## CLI

With the `cli` feature:

```bash
cargo run --features cli -- "hello world"
# Input:  hello world
# Output: HELLO WORLD
# Length: 11

cargo run --features cli -- -p ">>" -s "<<" "hello"
# Input:  hello
# Output: >>HELLO<<
# Length: 7
```

## Development

```bash
# Run tests
cargo test

# Run with output
cargo test -- --nocapture

# Run benchmarks
cargo bench

# Lint with clippy
cargo clippy -- -D warnings

# Format
cargo fmt

# Build
cargo build --release
```

## License

MIT
