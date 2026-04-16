package example

import (
	"strings"
	"testing"
)

func BenchmarkProcess(b *testing.B) {
	s := New(WithPrefix(">>"), WithSuffix("<<"))
	input := strings.Repeat("hello world ", 10)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = s.Process(input)
	}
}

func BenchmarkProcessSimple(b *testing.B) {
	s := New()
	input := "hello world"

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = s.Process(input)
	}
}
