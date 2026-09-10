#!/usr/bin/env python3
"""Add rendered per-sentence hard line breaks to Markdown or AsciiDoc prose.

Markdown: append <br> after sentence endings.
AsciiDoc: split sentences onto physical lines and append ` +` at line end.

This is a conservative best-effort converter. It protects common code blocks,
tables, front matter, and structural markup, but complex documents should still be
rendered and checked.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

MD_EXTS = {".md", ".markdown", ".mdown", ".mkd"}
ADOC_EXTS = {".adoc", ".asciidoc", ".asc"}

CLOSERS = set('」』）)]｝}】〉》"\'”’')
J_ENDERS = set("。！？")
E_ENDERS = set("!?．")
COMMON_ABBREVIATIONS = {
    "mr.", "mrs.", "ms.", "dr.", "prof.", "sr.", "jr.", "st.",
    "vs.", "etc.", "e.g.", "i.e.", "cf.", "fig.", "no.", "vol.",
    "dept.", "inc.", "ltd.", "co.", "corp.", "u.s.", "u.k.", "u.n.",
}

MD_BR_RE = re.compile(r"\s*<br\s*/?>", re.IGNORECASE)
ADOC_HARDBREAK_RE = re.compile(r"\s\+$")


def detect_format(path: Path, explicit: str) -> str:
    if explicit != "auto":
        return explicit
    suffix = path.suffix.lower()
    if suffix in MD_EXTS:
        return "markdown"
    if suffix in ADOC_EXTS:
        return "asciidoc"
    raise SystemExit(
        f"Cannot infer format from extension {suffix!r}. Use --format markdown or --format asciidoc."
    )


def _line_has_url_like_token(text: str, period_index: int) -> bool:
    """Return True if the period likely belongs to a URL/domain/email-ish token."""
    left = text[max(0, period_index - 40):period_index]
    right = text[period_index + 1:period_index + 40]
    token_left = re.search(r"[A-Za-z0-9_:/@%+~#?&=-]+$", left)
    token_right = re.match(r"[A-Za-z0-9_:/@%+~#?&=-]+", right)
    token = (token_left.group(0) if token_left else "") + "." + (token_right.group(0) if token_right else "")
    return bool(
        re.search(r"https?://|www\.|\b[\w.-]+@[\w.-]+\.\w+", token)
        or re.search(r"\b[A-Za-z0-9-]+\.[A-Za-z]{2,}\b", token)
    )


def _period_is_sentence_end(text: str, i: int) -> bool:
    prev_ch = text[i - 1] if i > 0 else ""
    next_ch = text[i + 1] if i + 1 < len(text) else ""

    # Decimal numbers: 3.14
    if prev_ch.isdigit() and next_ch.isdigit():
        return False

    # Ellipsis: handle the final period only.
    if next_ch == ".":
        return False

    if _line_has_url_like_token(text, i):
        return False

    prefix = text[: i + 1].lower()
    for abbr in COMMON_ABBREVIATIONS:
        if prefix.endswith(abbr):
            return False

    # Initialisms such as U.S. or A.I. are usually not reliable sentence ends.
    if re.search(r"(?:\b[A-Za-z]\.){2,}$", prefix):
        return False

    # Treat as a sentence end at end-of-line, before whitespace, or before a closer.
    if not next_ch or next_ch.isspace() or next_ch in CLOSERS:
        return True

    return False


def _is_sentence_ender(text: str, i: int) -> bool:
    ch = text[i]
    if ch in J_ENDERS or ch in E_ENDERS:
        return True
    if ch == ".":
        return _period_is_sentence_end(text, i)
    return False


def strip_markdown_markers(text: str) -> str:
    # Remove existing <br> markers where they are likely already serving this skill.
    return MD_BR_RE.sub(" ", text).strip()


def strip_asciidoc_marker(text: str) -> str:
    return ADOC_HARDBREAK_RE.sub("", text.rstrip()).strip()


def split_sentences(text: str) -> List[str]:
    """Split prose into sentences using CJK-friendly and English-friendly heuristics."""
    text = text.strip()
    if not text:
        return []

    sentences: List[str] = []
    start = 0
    i = 0
    n = len(text)

    while i < n:
        if _is_sentence_ender(text, i):
            j = i + 1

            # Consume repeated sentence punctuation: ?!, ！？, etc.
            while j < n and (text[j] in J_ENDERS or text[j] in E_ENDERS or text[j] == "."):
                j += 1

            # Consume closing brackets/quotes.
            while j < n and text[j] in CLOSERS:
                j += 1

            piece = text[start:j].strip()
            if piece:
                sentences.append(piece)

            while j < n and text[j].isspace():
                j += 1
            start = j
            i = j
            continue
        i += 1

    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def add_md_breaks_to_text(text: str, mark_final: bool = True, source_split: bool = True) -> str:
    clean = strip_markdown_markers(text)
    sentences = split_sentences(clean)
    if not sentences:
        return text

    rendered: List[str] = []
    for idx, sentence in enumerate(sentences):
        needs_marker = mark_final or idx < len(sentences) - 1
        rendered.append(sentence + ("<br>" if needs_marker else ""))

    sep = "\n" if source_split else ""
    return sep.join(rendered)


def add_adoc_breaks_to_text(text: str, mark_final: bool = True) -> str:
    clean = strip_asciidoc_marker(text)
    sentences = split_sentences(clean)
    if not sentences:
        return text.rstrip()

    rendered: List[str] = []
    for idx, sentence in enumerate(sentences):
        needs_marker = mark_final or idx < len(sentences) - 1
        rendered.append(sentence + (" +" if needs_marker else ""))
    return "\n".join(rendered)


MD_LIST_RE = re.compile(r"^(?P<prefix>\s*(?:>\s*)*(?:[-+*]|\d+[.)])\s+(?:\[[ xX]\]\s+)?)")
MD_BLOCKQUOTE_RE = re.compile(r"^(?P<prefix>\s*(?:>\s*)+)(?P<body>.*)$")
ADOC_LIST_RE = re.compile(r"^\s*(?:[*.-]+|\d+\.|[a-zA-Z]\.)(?:\s+|$)")


def _is_markdown_table_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("|") and stripped.endswith("|"):
        return True
    if re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$", stripped):
        return True
    return False


def _is_markdown_structural_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if re.match(r"^#{1,6}\s+", stripped):
        return True
    if re.match(r"^(?:-{3,}|\*{3,}|_{3,})\s*$", stripped):
        return True
    if re.match(r"^\[[^\]]+\]:\s+", stripped):
        return True
    if stripped.startswith("<!--") or stripped.endswith("-->"):
        return True
    if stripped.startswith("<") and not stripped.lower().startswith("<br"):
        return True
    if stripped.startswith("!["):
        return True
    if _is_markdown_table_line(line):
        return True
    # Four-space indented code block.
    if re.match(r"^(?: {4}|\t)", line):
        return True
    return False


def transform_markdown(text: str, mark_final: bool = True, include_list_items: bool = True) -> str:
    lines = text.splitlines()
    trailing_newline = text.endswith("\n")
    out: List[str] = []
    in_fence = False
    fence_marker = ""
    in_front_matter = False
    front_delim = ""

    for line_no, line in enumerate(lines):
        stripped = line.strip()

        # Front matter at top of file.
        if line_no == 0 and stripped in {"---", "+++"}:
            in_front_matter = True
            front_delim = stripped
            out.append(line)
            continue
        if in_front_matter:
            out.append(line)
            if line_no > 0 and stripped == front_delim:
                in_front_matter = False
            continue

        # Fenced code blocks.
        fence_match = re.match(r"^\s*(```+|~~~+)", line)
        if fence_match:
            marker = fence_match.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
            out.append(line)
            continue
        if in_fence or _is_markdown_structural_line(line):
            out.append(line)
            continue

        list_match = MD_LIST_RE.match(line)
        if list_match:
            if not include_list_items:
                out.append(line)
                continue
            prefix = list_match.group("prefix")
            body = line[len(prefix):]
            converted = add_md_breaks_to_text(body, mark_final=mark_final, source_split=False)
            out.append(prefix + converted)
            continue

        quote_match = MD_BLOCKQUOTE_RE.match(line)
        if quote_match:
            prefix = quote_match.group("prefix")
            body = quote_match.group("body")
            converted = add_md_breaks_to_text(body, mark_final=mark_final, source_split=True)
            out.extend(prefix + part for part in converted.split("\n"))
            continue

        converted = add_md_breaks_to_text(line, mark_final=mark_final, source_split=True)
        out.extend(converted.split("\n"))

    result = "\n".join(out)
    if trailing_newline:
        result += "\n"
    return result


def _is_adoc_delimiter(line: str) -> bool:
    stripped = line.strip()
    return bool(re.match(r"^(?:-{4,}|\.{4,}|={4,}|\*{4,}|_{4,}|\+{4,}|/{4,}|--)$", stripped))


def _is_adoc_structural_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if re.match(r"^={1,6}\s+", stripped):
        return True
    if re.match(r"^\[[^\]]*\]$", stripped):
        return True
    if re.match(r"^:[A-Za-z0-9_-]+:.*$", stripped):
        return True
    if stripped.startswith("//"):
        return True
    if re.match(r"^\.[^\s.].*", stripped):
        return True
    if re.match(r"^[|!,]?===\s*$", stripped):
        return True
    if stripped.startswith(("|", "!", ",")):
        return True
    if re.match(r"^(?:include|image|link|xref|ifdef|ifndef|endif)::?", stripped):
        return True
    if re.match(r"^(?:NOTE|TIP|IMPORTANT|WARNING|CAUTION):\s+", stripped):
        return True
    return False


def transform_asciidoc(text: str, mark_final: bool = True, include_list_items: bool = False) -> str:
    lines = text.splitlines()
    trailing_newline = text.endswith("\n")
    out: List[str] = []
    in_delimited = False
    delimiter = ""

    for line in lines:
        stripped = line.strip()
        if _is_adoc_delimiter(line):
            if not in_delimited:
                in_delimited = True
                delimiter = stripped
            elif stripped == delimiter:
                in_delimited = False
            out.append(line)
            continue

        if in_delimited or _is_adoc_structural_line(line):
            out.append(line)
            continue

        if ADOC_LIST_RE.match(line) and not include_list_items:
            out.append(line)
            continue

        converted = add_adoc_breaks_to_text(line, mark_final=mark_final)
        out.extend(converted.split("\n"))

    result = "\n".join(out)
    if trailing_newline:
        result += "\n"
    return result


def transform_text(text: str, fmt: str, mark_final: bool, include_list_items: bool) -> str:
    if fmt == "markdown":
        return transform_markdown(text, mark_final=mark_final, include_list_items=include_list_items)
    if fmt == "asciidoc":
        return transform_asciidoc(text, mark_final=mark_final, include_list_items=include_list_items)
    raise ValueError(f"Unsupported format: {fmt}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Input Markdown or AsciiDoc file")
    parser.add_argument("--format", choices=["auto", "markdown", "asciidoc"], default="auto")
    parser.add_argument("--output", "-o", type=Path, help="Output path. Defaults to stdout unless --in-place is used.")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the input file")
    parser.add_argument("--backup-suffix", default="", help="When --in-place is used, copy the original to INPUT + suffix")
    parser.add_argument("--skip-final", action="store_true", help="Do not add a hard-break marker after the final sentence of a processed line/paragraph")
    parser.add_argument("--include-list-items", action="store_true", help="Also process list-item lines. Markdown is usually safe; AsciiDoc list rendering should be checked.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    fmt = detect_format(args.input, args.format)
    input_text = args.input.read_text(encoding="utf-8")
    output_text = transform_text(
        input_text,
        fmt=fmt,
        mark_final=not args.skip_final,
        include_list_items=args.include_list_items or fmt == "markdown",
    )

    if args.in_place:
        if args.output:
            parser.error("--output cannot be used with --in-place")
        if args.backup_suffix:
            backup_path = Path(str(args.input) + args.backup_suffix)
            shutil.copy2(args.input, backup_path)
        args.input.write_text(output_text, encoding="utf-8")
        return 0

    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
    else:
        sys.stdout.write(output_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
