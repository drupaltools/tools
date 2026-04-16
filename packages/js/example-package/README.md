# @monorepo/example-package

Example TypeScript package from the polyglot monorepo.

## Installation

```bash
npm install @monorepo/example-package
# or
pnpm add @monorepo/example-package
# or
yarn add @monorepo/example-package
```

## Usage

```typescript
import { ExampleService } from '@monorepo/example-package';

const service = new ExampleService({ prefix: '>>' });
const result = service.process('hello');
// result.value === '>>HELLO'
// result.length === 7
```

## Scripts

| Command              | Description                    |
| -------------------- | ------------------------------ |
| `pnpm build`         | Build with tsup                |
| `pnpm test`          | Run tests with Vitest          |
| `pnpm test:coverage` | Run tests with coverage report |
| `pnpm lint`          | Run ESLint                     |
| `pnpm format`        | Format with Prettier           |
| `pnpm format:check`  | Check formatting               |
| `pnpm typecheck`     | Run TypeScript type checking   |
| `pnpm all`           | Run all checks and build       |

## License

MIT
