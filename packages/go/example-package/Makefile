.PHONY: all test test-verbose lint lint-fix fmt build clean bench help

BINARY_NAME=example
GO=go
GOFLAGS=-v
TESTFLAGS=-race -v
LINTFLAGS=./...

all: lint test build

test:
	$(GO) test $(GOFLAGS) -run Test ./...

test-verbose:
	$(GO) test $(TESTFLAGS) -coverprofile=coverage.out ./...

bench:
	$(GO) test -bench=. -benchmem ./...

lint:
	golangci-lint run $(LINTFLAGS)

lint-fix:
	golangci-lint run --fix $(LINTFLAGS)

fmt:
	go fmt ./...

vet:
	go vet ./...

build:
	$(GO) build -o $(BINARY_NAME) ./cmd/example

build-all:
	GOOS=linux GOARCH=amd64 $(GO) build -o $(BINARY_NAME)-linux-amd64 ./cmd/example
	GOOS=darwin GOARCH=amd64 $(GO) build -o $(BINARY_NAME)-darwin-amd64 ./cmd/example
	GOOS=windows GOARCH=amd64 $(GO) build -o $(BINARY_NAME).exe ./cmd/example

clean:
	rm -f $(BINARY_NAME) $(BINARY_NAME)-* coverage.out

coverage: test-verbose
	go tool cover -html=coverage.out -o coverage.html

help:
	@echo "Available targets:"
	@echo "  all          - Run lint, test, and build"
	@echo "  test         - Run tests"
	@echo "  test-verbose - Run tests with verbose output and coverage"
	@echo "  bench        - Run benchmarks"
	@echo "  lint         - Run golangci-lint"
	@echo "  lint-fix     - Run golangci-lint with auto-fix"
	@echo "  fmt          - Format code"
	@echo "  vet          - Run go vet"
	@echo "  build        - Build binary"
	@echo "  build-all    - Build for all platforms"
	@echo "  clean        - Remove build artifacts"
	@echo "  coverage     - Generate HTML coverage report"
