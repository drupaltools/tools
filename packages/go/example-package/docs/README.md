# example-package

Example Go module from the polyglot monorepo.

## Installation

```bash
go get github.com/drupaltools/tools/packages/go/example-package
```

## Usage

```go
package main

import (
    "fmt"
    "github.com/drupaltools/tools/packages/go/example-package/example"
)

func main() {
    svc := example.New(example.WithPrefix(">>"))
    result, err := svc.Process("hello")
    if err != nil {
        panic(err)
    }
    fmt.Println(result.Value) // >>HELLO
}
```

## CLI Tool

```bash
make build
./example "hello world"
# Input:  hello world
# Output: HELLO WORLD
# Length: 11

./example -prefix ">>" -suffix "<<" "hello"
# Input:  hello
# Output: >>HELLO<<
# Length: 7
```

## Make Targets

| Target          | Description              |
| --------------- | ------------------------ |
| `make test`     | Run tests                |
| `make lint`     | Run golangci-lint        |
| `make fmt`      | Format code              |
| `make build`    | Build binary             |
| `make bench`    | Run benchmarks           |
| `make coverage` | Generate coverage report |

## License

MIT
