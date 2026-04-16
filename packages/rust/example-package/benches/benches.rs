//! Benchmarks for the example package.

use criterion::{black_box, criterion_group, criterion_main, Criterion};
use example_package::ExampleService;

fn bench_process_simple(c: &mut Criterion) {
    let service = ExampleService::new();
    c.bench_function("process_simple", |b| {
        b.iter(|| {
            let _ = service.process(black_box("hello world"));
        });
    });
}

fn bench_process_with_options(c: &mut Criterion) {
    let service = ExampleService::new().prefix(">>").suffix("<<");
    c.bench_function("process_with_options", |b| {
        b.iter(|| {
            let _ = service.process(black_box("hello world"));
        });
    });
}

fn bench_process_custom_transform(c: &mut Criterion) {
    let service = ExampleService::new().transform(|s| s.to_uppercase());
    c.bench_function("process_custom_transform", |b| {
        b.iter(|| {
            let _ = service.process(black_box("hello world"));
        });
    });
}

criterion_group!(
    benches,
    bench_process_simple,
    bench_process_with_options,
    bench_process_custom_transform
);
criterion_main!(benches);
