// Command-line tool for example-package.
package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/drupaltools/tools/packages/go/example-package/example"
)

var (
	prefix  = flag.String("prefix", "", "Prefix for processed output")
	suffix  = flag.String("suffix", "", "Suffix for processed output")
	reverse = flag.Bool("reverse", false, "Reverse the input")
)

func main() {
	flag.Parse()

	args := flag.Args()
	if len(args) == 0 {
		fmt.Println("Usage: example [flags] <input>")
		flag.PrintDefaults()
		os.Exit(1)
	}

	input := strings.Join(args, " ")
	opts := []example.Option{}

	if *prefix != "" {
		opts = append(opts, example.WithPrefix(*prefix))
	}
	if *suffix != "" {
		opts = append(opts, example.WithSuffix(*suffix))
	}
	if *reverse {
		opts = append(opts, example.WithTransform(func(s string) string {
			runes := []rune(s)
			for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
				runes[i], runes[j] = runes[j], runes[i]
			}
			return string(runes)
		}))
	}

	svc := example.New(opts...)
	result, err := svc.Process(input)
	if err != nil {
		log.Fatalf("Error: %v", err)
	}

	fmt.Printf("Input:  %s\n", result.Metadata.Original)
	fmt.Printf("Output: %s\n", result.Value)
	fmt.Printf("Length: %d\n", result.Length)
}
