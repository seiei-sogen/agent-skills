package main

import (
	"bytes"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func TestDefaultOutputPath(t *testing.T) {
	t.Parallel()

	if got, want := defaultOutputPath("docs/guide.adoc"), "docs/guide.html"; got != want {
		t.Fatalf("defaultOutputPath() = %q, want %q", got, want)
	}
	if got, want := defaultOutputPath("docs/guide"), "docs/guide.html"; got != want {
		t.Fatalf("defaultOutputPath() = %q, want %q", got, want)
	}
}

func TestDocumentTitle(t *testing.T) {
	t.Parallel()

	if got, want := documentTitle([]byte("= 変換ガイド\n\n本文\n"), "guide.adoc"), "変換ガイド"; got != want {
		t.Fatalf("documentTitle() = %q, want %q", got, want)
	}
	if got, want := documentTitle([]byte("本文だけ\n"), "fallback.adoc"), "fallback"; got != want {
		t.Fatalf("documentTitle() fallback = %q, want %q", got, want)
	}
}

func TestStandaloneHTMLContainsEmbeddedTheme(t *testing.T) {
	t.Parallel()

	document := standaloneHTML("A < B", "ja", "<p>本文</p>")
	for _, expected := range []string{
		"<title>A &lt; B</title>",
		"<style>",
		"--color-primary",
		"<article class=\"doc\">",
		"<p>本文</p>",
	} {
		if !strings.Contains(document, expected) {
			t.Errorf("standaloneHTML() does not contain %q", expected)
		}
	}
	if strings.Contains(document, "<link rel=\"stylesheet\"") {
		t.Error("standaloneHTML() contains an external stylesheet link")
	}
}

func TestWriteOutputRequiresForce(t *testing.T) {
	t.Parallel()

	output := filepath.Join(t.TempDir(), "output.html")
	if err := writeOutput(output, []byte("first"), false); err != nil {
		t.Fatal(err)
	}
	if err := writeOutput(output, []byte("second"), false); err == nil {
		t.Fatal("writeOutput() replaced an existing file without force")
	}
	if err := writeOutput(output, []byte("second"), true); err != nil {
		t.Fatal(err)
	}
	content, err := os.ReadFile(output)
	if err != nil {
		t.Fatal(err)
	}
	if got, want := string(content), "second"; got != want {
		t.Fatalf("output = %q, want %q", got, want)
	}
}

func TestRunWithAsciidoctor(t *testing.T) {
	if _, err := exec.LookPath("asciidoctor"); err != nil {
		t.Skip("asciidoctor is not installed")
	}

	directory := t.TempDir()
	input := filepath.Join(directory, "sample.adoc")
	output := filepath.Join(directory, "sample.html")
	source := `= サンプル

== 概要

NOTE: CSSを埋め込んだHTMLです。

[source,go]
----
fmt.Println("hello")
----
`
	if err := os.WriteFile(input, []byte(source), 0o644); err != nil {
		t.Fatal(err)
	}

	var stdout bytes.Buffer
	var stderr bytes.Buffer
	if err := run([]string{"-output", output, input}, &stdout, &stderr); err != nil {
		t.Fatalf("run() error = %v, stderr = %s", err, stderr.String())
	}
	content, err := os.ReadFile(output)
	if err != nil {
		t.Fatal(err)
	}
	html := string(content)
	for _, expected := range []string{"<style>", "サンプル", "admonitionblock", "fmt.Println"} {
		if !strings.Contains(html, expected) {
			t.Errorf("generated HTML does not contain %q", expected)
		}
	}
}
