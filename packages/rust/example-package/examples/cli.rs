//! CLI example for the example package.

#[cfg(feature = "cli")]
use clap::Parser;
use example_package::{ExampleService, ProcessOptions};

#[cfg(feature = "cli")]
#[derive(Parser, Debug)]
#[command(name = "example-package", about = "CLI tool for example-package")]
struct Args {
    /// Input string to process
    input: String,

    /// Prefix to add to output
    #[arg(short, long)]
    prefix: Option<String>,

    /// Suffix to add to output
    #[arg(short, long)]
    suffix: Option<String>,

    /// Reverse the input
    #[arg(long)]
    reverse: bool,
}

#[cfg(feature = "cli")]
fn main() {
    let args = Args::parse();

    let mut options = ProcessOptions::new();
    if let Some(ref p) = args.prefix {
        options = options.with_prefix(p);
    }
    if let Some(ref s) = args.suffix {
        options = options.with_suffix(s);
    }
    if args.reverse {
        options = options.with_transform(|s| s.chars().rev().collect());
    }

    let service = ExampleService::with_options(options);
    match service.process(&args.input) {
        Ok(result) => {
            println!("Input:  {}", result.metadata.original);
            println!("Output: {}", result.value);
            println!("Length: {}", result.length);
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    }
}

#[cfg(not(feature = "cli"))]
fn main() {
    eprintln!("This binary requires the 'cli' feature. Run with: cargo run --features cli");
    std::process::exit(1);
}
