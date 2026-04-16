// Package example provides a string processing service for the monorepo.
package example

import (
	"fmt"
	"strings"
	"time"
)

// ProcessMetadata contains metadata about a processed input.
type ProcessMetadata struct {
	Original    string
	ProcessedAt time.Time
}

// ProcessResult represents the result of processing a string.
type ProcessResult struct {
	Value    string
	Length   int
	Metadata ProcessMetadata
}

// Service handles string processing with configurable options.
type Service struct {
	prefix    string
	suffix    string
	transform func(string) string
}

// Option configures the Service.
type Option func(*Service)

// WithPrefix sets the prefix for processed values.
func WithPrefix(prefix string) Option {
	return func(s *Service) {
		s.prefix = prefix
	}
}

// WithSuffix sets the suffix for processed values.
func WithSuffix(suffix string) Option {
	return func(s *Service) {
		s.suffix = suffix
	}
}

// WithTransform sets a custom transform function.
func WithTransform(fn func(string) string) Option {
	return func(s *Service) {
		s.transform = fn
	}
}

// New creates a new Service with the given options.
func New(opts ...Option) *Service {
	s := &Service{
		transform: strings.ToUpper,
	}
	for _, opt := range opts {
		opt(s)
	}
	return s
}

// Process transforms the input string and returns a ProcessResult.
func (s *Service) Process(input string) (*ProcessResult, error) {
	if strings.TrimSpace(input) == "" {
		return nil, fmt.Errorf("input cannot be empty")
	}

	transformed := s.transform(input)
	value := s.prefix + transformed + s.suffix

	return &ProcessResult{
		Value:  value,
		Length: len(value),
		Metadata: ProcessMetadata{
			Original:    input,
			ProcessedAt: time.Now().UTC(),
		},
	}, nil
}

// Reset clears any internal state (no-op for current implementation).
func (s *Service) Reset() {
	// No internal state to reset
}
