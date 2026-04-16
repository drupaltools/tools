export interface ExampleOptions {
  prefix?: string;
  suffix?: string;
  transform?: (input: string) => string;
}

export interface ProcessResult {
  value: string;
  length: number;
  metadata: {
    original: string;
    processedAt: Date;
  };
}

export type TransformFn = (input: string) => string;
