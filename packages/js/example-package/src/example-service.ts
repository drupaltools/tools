import type { ExampleOptions, ProcessResult, TransformFn } from './types.js';

export class ExampleService {
  private readonly transform: TransformFn;

  constructor(private readonly options: ExampleOptions = {}) {
    this.transform = options.transform ?? ((s: string) => s.toUpperCase());
  }

  process(input: string): ProcessResult {
    if (!input) {
      throw new Error('Input cannot be empty');
    }

    const transformed = this.transform(input);
    const prefixed =
      this.options.prefix !== undefined ? `${this.options.prefix}${transformed}` : transformed;
    const suffixed =
      this.options.suffix !== undefined ? `${prefixed}${this.options.suffix}` : prefixed;

    return {
      value: suffixed,
      length: suffixed.length,
      metadata: {
        original: input,
        processedAt: new Date(),
      },
    };
  }

  reset(): void {
    // Reset state if needed
  }
}
