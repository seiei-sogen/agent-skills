from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sentence_linebreak as slb


def test_markdown_sample_matches_expected():
    sample = (ROOT / "examples" / "sample.md").read_text(encoding="utf-8")
    expected = (ROOT / "examples" / "expected.md").read_text(encoding="utf-8")
    assert slb.transform_markdown(sample) == expected


def test_asciidoc_sample_matches_expected():
    sample = (ROOT / "examples" / "sample.adoc").read_text(encoding="utf-8")
    expected = (ROOT / "examples" / "expected.adoc").read_text(encoding="utf-8")
    assert slb.transform_asciidoc(sample) == expected


def test_markdown_is_idempotent():
    expected = (ROOT / "examples" / "expected.md").read_text(encoding="utf-8")
    assert slb.transform_markdown(expected) == expected


def test_asciidoc_is_idempotent():
    expected = (ROOT / "examples" / "expected.adoc").read_text(encoding="utf-8")
    assert slb.transform_asciidoc(expected) == expected


def test_decimal_and_common_abbreviation_are_not_split():
    text = "値は3.14です。Dr. Smith wrote this. 次です。"
    assert slb.split_sentences(text) == ["値は3.14です。", "Dr. Smith wrote this.", "次です。"]
