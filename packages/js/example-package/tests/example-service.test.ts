import { describe, it, expect, beforeEach } from 'vitest';
import { ExampleService } from '../src/example-service.js';

describe('ExampleService', () => {
  let service: ExampleService;

  beforeEach(() => {
    service = new ExampleService({ prefix: 'test:' });
  });

  describe('process', () => {
    it('should return prefixed uppercase result', () => {
      const result = service.process('hello world');

      expect(result.value).toBe('test:HELLO WORLD');
      expect(result.length).toBe(17);
      expect(result.metadata.original).toBe('hello world');
    });

    it('should include timestamp in metadata', () => {
      const result = service.process('test');

      expect(result.metadata.processedAt).toBeInstanceOf(Date);
    });

    it('should apply custom suffix when provided', () => {
      const customService = new ExampleService({ prefix: '>>', suffix: '<<' });
      const result = customService.process('x');

      expect(result.value).toBe('>>X<<');
    });

    it('should use custom transform function', () => {
      const customService = new ExampleService({
        transform: (s) => s.split('').reverse().join(''),
      });
      const result = customService.process('abc');

      expect(result.value).toBe('CBA');
    });

    it('should throw on empty input', () => {
      expect(() => service.process('')).toThrow('Input cannot be empty');
    });
  });

  describe('reset', () => {
    it('should reset state', () => {
      service.process('test');
      expect(() => service.reset()).not.toThrow();
    });
  });
});
