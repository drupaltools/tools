package example

import (
	"testing"
)

func TestNew(t *testing.T) {
	s := New()
	if s == nil {
		t.Fatal("New() returned nil")
	}
}

func TestService_Process(t *testing.T) {
	tests := []struct {
		name      string
		prefix    string
		suffix    string
		input     string
		wantValue string
		wantLen   int
		wantErr   bool
	}{
		{
			name:      "uppercase default",
			input:     "hello world",
			wantValue: "HELLO WORLD",
			wantLen:   11,
			wantErr:   false,
		},
		{
			name:      "with prefix",
			prefix:    ">>",
			input:     "foo",
			wantValue: ">>FOO",
			wantLen:   5,
			wantErr:   false,
		},
		{
			name:      "with suffix",
			suffix:    "<<",
			input:     "bar",
			wantValue: "BAR<<",
			wantLen:   5,
			wantErr:   false,
		},
		{
			name:      "with prefix and suffix",
			prefix:    ">>",
			suffix:    "<<",
			input:     "baz",
			wantValue: ">>BAZ<<",
			wantLen:   7,
			wantErr:   false,
		},
		{
			name:    "empty string",
			input:   "",
			wantErr: true,
		},
		{
			name:    "whitespace only",
			input:   "   ",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			opts := []Option{}
			if tt.prefix != "" {
				opts = append(opts, WithPrefix(tt.prefix))
			}
			if tt.suffix != "" {
				opts = append(opts, WithSuffix(tt.suffix))
			}
			s := New(opts...)

			got, err := s.Process(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("Process() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if tt.wantErr {
				return
			}
			if got.Value != tt.wantValue {
				t.Errorf("Process() value = %v, want %v", got.Value, tt.wantValue)
			}
			if got.Length != tt.wantLen {
				t.Errorf("Process() length = %v, want %v", got.Length, tt.wantLen)
			}
			if got.Metadata.Original != tt.input {
				t.Errorf("Process() original = %v, want %v", got.Metadata.Original, tt.input)
			}
		})
	}
}

func TestService_Process_CustomTransform(t *testing.T) {
	s := New(WithTransform(func(s string) string {
		return s + s // duplicate
	}))
	got, err := s.Process("x")
	if err != nil {
		t.Fatalf("Process() error = %v", err)
	}
	if got.Value != "xx" {
		t.Errorf("Process() value = %v, want %v", got.Value, "xx")
	}
}

func TestService_Reset(t *testing.T) {
	s := New()
	s.Process("test")
	s.Reset() // Should not panic
}
