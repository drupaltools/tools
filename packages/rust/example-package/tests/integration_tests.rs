//! Integration tests for the example package.

use example_package::{ExampleService, ProcessOptions};

#[test]
fn test_full_pipeline_with_all_options() {
    let service = ExampleService::with_options(
        ProcessOptions::new()
            .with_prefix(">>")
            .with_suffix("<<")
            .with_transform(|s| s.chars().rev().collect()),
    );
    let result = service.process("abc").unwrap();

    assert_eq!(result.value, ">>cba<<");
    assert_eq!(result.length, 7);
    assert_eq!(result.metadata.original, "abc");
}

#[test]
fn test_multiple_services_are_independent() {
    let service1 = ExampleService::new().prefix("A:");
    let service2 = ExampleService::new().prefix("B:");

    let r1 = service1.process("x").unwrap();
    let r2 = service2.process("x").unwrap();

    assert_eq!(r1.value, "A:X");
    assert_eq!(r2.value, "B:X");
}
