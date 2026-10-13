#!/usr/bin/env python3
"""easy-*.html が手本と同じ骨組みを持つかを検査する。

使い方:
    python3 check_easy_html.py <easy-xxx.html>

終了コード 0 なら合格。失敗した項目を 1 行ずつ出す。
"""

import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.counts = {}
        self.stack = []
        self.in_code = 0
        self.h2 = []
        self.current_h2 = None
        self.text_in_code = []
        self.in_p = False
        self.p_text = ""
        self.p_plain = ""
        self.long_paragraphs = []
        self.long_sentences = []
        self.figures_without_caption = 0
        self.in_figure = False
        self.figure_has_caption = False
        self.errors = []

    def start(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "").split()
        self.counts[tag] = self.counts.get(tag, 0) + 1
        if cls:
            key = tag + "." + ".".join(cls)
            self.counts[key] = self.counts.get(key, 0) + 1
        if tag == "code":
            self.in_code += 1
        if tag == "h2":
            self.current_h2 = ""
        if tag == "p":
            self.in_p, self.p_text, self.p_plain = True, "", ""
        if tag == "figure":
            self.in_figure, self.figure_has_caption = True, False
        if tag == "figcaption" and self.in_figure:
            self.figure_has_caption = True
        if tag == "svg":
            if "viewBox" not in a and "viewbox" not in a:
                self.errors.append("svg に viewBox がない")
            if "aria-label" not in a:
                self.errors.append("svg に aria-label がない")
        if tag in ("rect", "path", "text", "circle", "line") and self.stack and "svg" in self.stack:
            style = a.get("style", "")
            if re.search(r"(fill|stroke)\s*:\s*#", style) or re.match(r"#", a.get("fill", "")) or re.match(r"#", a.get("stroke", "")):
                self.errors.append(f"svg の <{tag}> に色が直書きされている（f-* クラスを使う）")
        self.stack.append(tag)

    def handle_starttag(self, tag, attrs):
        self.start(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.start(tag, attrs)
        self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "code":
            self.in_code -= 1
        if tag == "h2" and self.current_h2 is not None:
            self.h2.append(self.current_h2.strip())
            self.current_h2 = None
        if tag == "p" and self.in_p:
            if self.p_text.count("。") > 4:
                self.long_paragraphs.append(self.p_text.strip()[:20])
            for sentence in self.p_plain.split("。"):
                if len(sentence.strip()) > MAX_SENTENCE:
                    self.long_sentences.append(sentence.strip()[:20])
            self.in_p = False
        if tag == "figure":
            if not self.figure_has_caption:
                self.figures_without_caption += 1
            self.in_figure = False
        while self.stack and self.stack[-1] != tag:
            self.stack.pop()
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.current_h2 is not None:
            self.current_h2 += data
        if self.in_code:
            self.text_in_code.append(data)
        if self.in_p:
            self.p_text += data
            if not self.in_code:
                self.p_plain += data


CJK = re.compile(r"[　-ヿ㐀-鿿＀-￯]")
# コードを除いた 1 文の上限。これを超える文は読点で 2 文に割る
MAX_SENTENCE = 60


def svg_overflows(raw: str):
    """箱の中の文字が箱より広い <text> を返す。幅の目安は日本語 1 文字 = フォントサイズ、英数字 = その 0.6 倍。"""
    found = []
    for svg in re.findall(r"<svg.*?</svg>", raw, re.S):
        rects = [
            tuple(float(v) for v in m)
            for m in re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg)
        ]
        for m in re.finditer(r"<text ([^>]*)>(.*?)</text>", svg, re.S):
            attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
            text = html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))
            size = float(attrs.get("font-size", 13))
            x, y = float(attrs.get("x", 0)), float(attrs.get("y", 0))
            width = sum(size if CJK.match(ch) else size * 0.6 for ch in text)
            boxes = [r for r in rects if r[0] <= x <= r[0] + r[2] and r[1] <= y <= r[1] + r[3]]
            if boxes and width > min(boxes, key=lambda r: r[2] * r[3])[2]:
                found.append(text[:30])
    return found


def main(path: Path) -> int:
    raw = path.read_text(encoding="utf-8")
    s = Scan()
    s.feed(raw)
    c = s.counts
    overflows = svg_overflows(raw)
    checks = [
        (path.name.startswith("easy-") and path.suffix == ".html", "ファイル名が easy-*.html である"),
        ('lang="ja"' in raw, "<html lang=\"ja\">"),
        ("<title>" in raw and "{{" not in raw, "title があり、テンプレートの {{ }} が残っていない"),
        ("prefers-color-scheme: dark" in raw and "--bg:" in raw, "配色が CSS 変数で、ダークモードの定義がある"),
        (c.get("h1", 0) == 1, "h1 が 1 つ"),
        (c.get("p.lead", 0) >= 1, "対象のパス・行数・コミットを書く .lead がある"),
        (c.get("div.oneline", 0) >= 1, "1 文の要約 .oneline がある"),
        (len(s.h2) >= 6, f"h2 が 6 つ以上ある（今 {len(s.h2)}）"),
        (all(re.match(r"\d+", h) for h in s.h2), "すべての h2 が番号 .num で始まる"),
        (c.get("span.ln", 0) >= 10, "行番号 .ln 付きのコード全文がある"),
        (c.get("span.mk", 0) >= 2, "コード全文に A〜 のセグメント見出し .mk が 2 つ以上ある"),
        (c.get("table", 0) >= 2, "表が 2 つ以上ある（文法表とことば早見表）"),
        (any("文法" in h for h in s.h2), "「文法」の節がある"),
        (any("ことば" in h or "用語" in h for h in s.h2), "「ことば早見表」の節がある"),
        (any("つまずき" in h for h in s.h2), "「つまずきやすい」の節がある"),
        (c.get("div.cmp", 0) >= 2, "Ruby と TS を並べる .cmp が 2 つ以上ある"),
        (c.get("svg", 0) >= 2, "SVG 図が 2 つ以上ある"),
        (s.figures_without_caption == 0, "すべての figure に figcaption がある"),
        (c.get("div.note", 0) + c.get("div.note.warn-n", 0) + c.get("div.note.ok-n", 0) >= 2, "補足 .note が 2 つ以上ある"),
        (not re.search(r"<code>[^<]*<(?!/code>|span|/span)", raw), "code の中の < がエスケープされている"),
        ("TypeScript でいうと" in raw, "「TypeScript でいうと」の対応がある"),
        ("未確認" in raw or "実際に" in raw or "確かめ" in raw, "実行して確かめた事実、または「未確認」の明記がある"),
        (not overflows, "SVG の箱から文字がはみ出していない: " + ", ".join(overflows)),
        (not s.long_paragraphs, "1 段落が 4 文以内: " + ", ".join(s.long_paragraphs)),
        (not s.long_sentences, f"コードを除いた 1 文が {MAX_SENTENCE} 字以内: " + ", ".join(s.long_sentences)),
        (c.get("div.plain", 0) >= 4, f"節の冒頭の「ひとことで言うと」.plain が 4 つ以上ある（今 {c.get('div.plain', 0)}）"),
        (c.get("div.goals", 0) >= 1, "冒頭に「読み終わるとわかること」.goals がある"),
        (c.get("div.step", 0) == 0 or c.get("p.ja", 0) >= 1, "SQL や実行結果に「日本語にすると」.ja が付いている"),
        (c.get("p.q", 0) >= 3, f"「つまずきやすい」が Q&A 形式（.q が 3 つ以上。今 {c.get('p.q', 0)}）"),
    ]
    failed = [label for ok, label in checks if not ok] + s.errors
    for label in failed:
        print(f"NG: {label}")
    print(f"{'OK' if not failed else 'FAIL'}: {path} ({len(checks) - len([1 for ok, _ in checks if not ok])}/{len(checks)} 項目)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
