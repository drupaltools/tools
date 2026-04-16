import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'tests/**',
        'node_modules/**',
        'dist/**',
        '**/*.config.ts',
        '**/vitest*.ts',
        'coverage/**',
      ],
    },
    setupFiles: ['./tests/setup.ts'],
  },
});
