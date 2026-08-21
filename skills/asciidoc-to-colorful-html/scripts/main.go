package main

import (
	"bytes"
	_ "embed"
	"errors"
	"flag"
	"fmt"
	"html"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
)

//go:embed theme.css
var themeCSS string

var languagePattern = regexp.MustCompile(`^[A-Za-z][A-Za-z0-9-]*$`)

func main() {
	if err := run(os.Args[1:], os.Stdout, os.Stderr); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}

func run(args []string, stdout, stderr io.Writer) error {
	flags := flag.NewFlagSet("asciidoc-to-colorful-html", flag.ContinueOnError)
	flags.SetOutput(stderr)

	output := flags.String("output", "", "output HTML path (default: input path with .html extension)")
	force := flags.Bool("force", false, "replace an existing output file")
	noDataURI := flags.Bool("no-data-uri", false, "keep image references external instead of embedding data URIs")
	language := flags.String("lang", "ja", "HTML language tag")
	asciidoctor := flags.String("asciidoctor", "asciidoctor", "asciidoctor executable")
	flags.Usage = func() {
		fmt.Fprintf(stderr, "Usage: %s [options] input.adoc\n\n", flags.Name())
		flags.PrintDefaults()
	}

	if err := flags.Parse(args); err != nil {
		if errors.Is(err, flag.ErrHelp) {
			return nil
		}
		return err
	}
	if flags.NArg() != 1 {
		flags.Usage()
		return fmt.Errorf("expected exactly one AsciiDoc input file")
	}
	if !languagePattern.MatchString(*language) {
		return fmt.Errorf("invalid HTML language tag %q", *language)
	}

	inputPath, err := filepath.Abs(flags.Arg(0))
	if err != nil {
		return fmt.Errorf("resolve input path: %w", err)
	}
	inputInfo, err := os.Stat(inputPath)
	if err != nil {
		return fmt.Errorf("read input %q: %w", inputPath, err)
	}
	if !inputInfo.Mode().IsRegular() {
		return fmt.Errorf("input %q is not a regular file", inputPath)
	}

	outputPath := *output
	if outputPath == "" {
		outputPath = defaultOutputPath(inputPath)
	}
	outputPath, err = filepath.Abs(outputPath)
	if err != nil {
		return fmt.Errorf("resolve output path: %w", err)
	}
	if filepath.Clean(inputPath) == filepath.Clean(outputPath) {
		return fmt.Errorf("output path must differ from input path")
	}
	if !*force {
		if _, err := os.Stat(outputPath); err == nil {
			return fmt.Errorf("output %q already exists; pass -force to replace it", outputPath)
		} else if !errors.Is(err, os.ErrNotExist) {
			return fmt.Errorf("inspect output %q: %w", outputPath, err)
		}
	}

	source, err := os.ReadFile(inputPath)
	if err != nil {
		return fmt.Errorf("read input %q: %w", inputPath, err)
	}
	body, warnings, err := convertAsciiDoc(*asciidoctor, inputPath, !*noDataURI)
	if err != nil {
		return err
	}
	if warnings != "" {
		fmt.Fprintln(stderr, warnings)
	}

	title := documentTitle(source, inputPath)
	document := standaloneHTML(title, *language, string(body))
	if err := writeOutput(outputPath, []byte(document), *force); err != nil {
		return err
	}

	fmt.Fprintln(stdout, outputPath)
	return nil
}

func defaultOutputPath(inputPath string) string {
	extension := filepath.Ext(inputPath)
	if extension == "" {
		return inputPath + ".html"
	}
	return strings.TrimSuffix(inputPath, extension) + ".html"
}

func convertAsciiDoc(asciidoctor, inputPath string, embedImages bool) ([]byte, string, error) {
	inputDir := filepath.Dir(inputPath)
	arguments := []string{
		"--no-header-footer",
		"--safe-mode", "safe",
		"--base-dir", inputDir,
		"--attribute", "showtitle",
	}
	if embedImages {
		arguments = append(arguments, "--attribute", "data-uri")
	}
	arguments = append(arguments, "--out-file", "-", filepath.Base(inputPath))

	command := exec.Command(asciidoctor, arguments...)
	command.Dir = inputDir
	var output bytes.Buffer
	var diagnostic bytes.Buffer
	command.Stdout = &output
	command.Stderr = &diagnostic

	if err := command.Run(); err != nil {
		message := strings.TrimSpace(diagnostic.String())
		if message == "" {
			message = err.Error()
		}
		return nil, "", fmt.Errorf("asciidoctor failed: %s", message)
	}
	if output.Len() == 0 {
		return nil, "", fmt.Errorf("asciidoctor produced empty output")
	}

	return output.Bytes(), strings.TrimSpace(diagnostic.String()), nil
}

func documentTitle(source []byte, inputPath string) string {
	text := strings.TrimPrefix(string(source), "\ufeff")
	for _, line := range strings.Split(text, "\n") {
		line = strings.TrimSpace(strings.TrimSuffix(line, "\r"))
		if strings.HasPrefix(line, "= ") {
			if title := strings.TrimSpace(strings.TrimPrefix(line, "= ")); title != "" {
				return title
			}
		}

	}

	base := filepath.Base(inputPath)
	return strings.TrimSuffix(base, filepath.Ext(base))
}

func standaloneHTML(title, language, body string) string {
	return "<!doctype html>\n" +
		"<html lang=\"" + html.EscapeString(language) + "\">\n" +
		"<head>\n" +
		"  <meta charset=\"utf-8\">\n" +
		"  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n" +
		"  <meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; img-src 'self' data: https: http:; style-src 'unsafe-inline'; font-src 'self' data:;\">\n" +
		"  <meta name=\"generator\" content=\"asciidoc-to-colorful-html\">\n" +
		"  <title>" + html.EscapeString(title) + "</title>\n" +
		"  <style>\n" + themeCSS + "\n  </style>\n" +
		"</head>\n" +
		"<body>\n" +
		"  <div class=\"page-frame\">\n" +
		"    <article class=\"doc\">\n" + body + "\n" +
		"    </article>\n" +
		"  </div>\n" +
		"</body>\n" +
		"</html>\n"
}

func writeOutput(path string, data []byte, force bool) error {
	if !force {
		file, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o644)
		if err != nil {
			return fmt.Errorf("create output %q: %w", path, err)
		}
		complete := false
		defer func() {
			if !complete {
				_ = os.Remove(path)
			}
		}()
		if _, err := file.Write(data); err != nil {
			_ = file.Close()
			return fmt.Errorf("write output %q: %w", path, err)
		}
		if err := file.Close(); err != nil {
			return fmt.Errorf("close output %q: %w", path, err)
		}
		complete = true
		return nil
	}

	temporary, err := os.CreateTemp(filepath.Dir(path), ".asciidoc-to-colorful-html-*.tmp")
	if err != nil {
		return fmt.Errorf("create temporary output: %w", err)
	}
	temporaryPath := temporary.Name()
	defer os.Remove(temporaryPath)

	if err := temporary.Chmod(0o644); err != nil {
		_ = temporary.Close()
		return fmt.Errorf("set temporary output permissions: %w", err)
	}
	if _, err := temporary.Write(data); err != nil {
		_ = temporary.Close()
		return fmt.Errorf("write temporary output: %w", err)
	}
	if err := temporary.Close(); err != nil {
		return fmt.Errorf("close temporary output: %w", err)
	}
	if err := os.Rename(temporaryPath, path); err != nil {
		return fmt.Errorf("replace output %q: %w", path, err)
	}
	return nil
}
