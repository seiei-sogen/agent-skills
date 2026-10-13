#!/usr/bin/env python3
"""railsguides.jp の PDF を章ごとの Markdown に変換する。

使い方:
    python3 pdf_to_markdown.py <rails-guide.pdf> <出力ディレクトリ>

依存: poppler の pdftohtml と pdfinfo、pdfminer.six。
PDF のしおり (outline) で章と見出しの階層を決め、pdftohtml -xml の
フォント情報で本文・インラインコード・コードブロックを見分ける。
"""

import html
import os
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import resolve1

HEADER_LIMIT = 75  # これより上の行はページ上部の柱 (running header)
FOOTER_LIMIT = 1215  # これより下の行はページ番号
BODY_PITCH = 34.5  # 本文の行送り (px)
CODE_PITCH = 17  # コードブロックの行送り (px)
CJK_RANGE = "　-ヿ㐀-鿿＀-￯"
CJK = re.compile(f"[{CJK_RANGE}]")
CJK_SPACE = re.compile(f"(?<=[{CJK_RANGE}]) +(?=[{CJK_RANGE}])")
COMMENT_SPACES = [  # コメント用フォントは字間に余計な空白が入るので、記号の前後だけ詰める
    (re.compile(r" (?=[.,:)])"), ""),
    (re.compile(r"(?<=[/_(]) "), ""),
    (re.compile(r" (?=[/_])"), ""),
    (re.compile(r"\. (?=[a-z])"), "."),
]
OPEN_BRACKET = "「（『【［〈《"
CLOSE_PUNCT = "」）』】］〉》、。，．："
ADMONITION = re.compile(r"^(NOTE|TIP|WARNING|INFO|IMPORTANT|CAUTION):\s*")
BULLET = re.compile(r"^([•–]|\d+\.)\s*")
TAG = re.compile(r"<[^>]+>")
FRAG = re.compile(
    r'<text top="(\d+)" left="(\d+)" width="(\d+)" height="(\d+)" font="(\d+)">(.*?)</text>'
)
FONTSPEC = re.compile(r'<fontspec id="(\d+)" size="(\d+)" family="([^"]*)"')
HREF = re.compile(r'<a href="([^"]*)">')


def read_outline(pdf: Path):
    """しおりを (level, title, page) のリストで返す。page は 1 始まり。"""
    with pdf.open("rb") as fp:
        doc = PDFDocument(PDFParser(fp))
        page_index = {p.pageid: i + 1 for i, p in enumerate(PDFPage.create_pages(doc))}
        entries = []
        for level, title, dest, action, _ in doc.get_outlines():
            if dest is None and action is not None:
                dest = resolve1(action).get("D")
            if isinstance(dest, (bytes, str)):
                dest = resolve1(doc.get_dest(dest))
            dest = resolve1(dest)
            if isinstance(dest, dict):
                dest = dest.get("D")
            page = page_index[resolve1(dest)[0].objid] if dest else None
            entries.append((level, title.strip(), page))
    return entries


def read_pages(pdf: Path, first: int, last: int):
    """pdftohtml -xml を1回走らせ、ページ番号 -> 断片リストを返す。"""
    out = Path(os.environ.get("TMPDIR", "/tmp")) / "rails-guide-xml"
    subprocess.run(
        ["pdftohtml", "-xml", "-i", "-q", "-f", str(first), "-l", str(last), str(pdf), str(out)],
        check=True,
    )
    xml = out.with_suffix(".xml").read_text(encoding="utf-8", errors="replace")
    fonts = {int(i): (int(size), family) for i, size, family in FONTSPEC.findall(xml)}
    pages = {}
    for number, body in re.findall(r'<page number="(\d+)".*?>(.*?)</page>', xml, re.S):
        frags = []
        for top, left, width, height, font, raw in FRAG.findall(body):
            size, family = fonts[int(font)]
            text = CJK_SPACE.sub("", html.unescape(TAG.sub("", raw)))
            if "LCIRCLE" in family or not text.strip():
                continue
            href = HREF.search(raw)
            link = html.unescape(href.group(1)) if href else None
            if link and "\ufffd" in link:
                link = link.split("#")[0]  # 文字化けしたアンカーは落とし、ページだけ残す
            if link and "\ufffd" in link:
                link = None  # パス自体が文字化けした URL は捨て、本文だけ残す
            frags.append(
                {
                    "top": int(top),
                    "left": int(left),
                    "width": int(width),
                    "height": int(height),
                    "font": int(font),
                    "size": size,
                    "mono": family == "Times",
                    "bold": raw.startswith("<b>"),
                    "href": link,
                    "text": text,
                }
            )
        pages[int(number)] = frags
    return pages


def group_lines(frags):
    """縦位置の近い断片を1行にまとめる。"""
    frags = sorted(frags, key=lambda f: (f["top"] + f["height"] / 2, f["left"]))
    lines = []
    for f in frags:
        center = f["top"] + f["height"] / 2
        if lines and abs(lines[-1]["center"] - center) <= 8:
            lines[-1]["frags"].append(f)
        else:
            lines.append({"center": center, "frags": [f]})
    for line in lines:
        line["frags"].sort(key=lambda f: f["left"])
        line["left"] = line["frags"][0]["left"]
    return lines


def needs_space(prev: str, nxt: str, gap: int) -> bool:
    if not prev or not nxt or gap <= 3:
        return False
    a, b = prev[-1], nxt[0]
    if CJK.match(a) and CJK.match(b):
        return False
    if a in OPEN_BRACKET or b in CLOSE_PUNCT:
        return False
    return True


def render_inline(frags) -> str:
    """1行の断片を Markdown のインライン表記に直す。"""
    runs = []  # [href, mono, text, left, right]
    for f in frags:
        text = f["text"]
        if runs and runs[-1][0] == f["href"] and runs[-1][1] == f["mono"] and f["href"] is not None:
            runs[-1][2] += (" " if needs_space(runs[-1][2], text, f["left"] - runs[-1][4]) else "") + text
            runs[-1][4] = f["left"] + f["width"]
        else:
            runs.append([f["href"], f["mono"], text, f["left"], f["left"] + f["width"]])
    out = ""
    prev_right = None
    prev_text = ""
    for href, mono, text, left, right in runs:
        shown = f"`{text}`" if mono else text
        if href:
            shown = f"[{shown}]({href})"
        if out and needs_space(prev_text, text, left - prev_right):
            out += " "
        out += shown
        prev_right, prev_text = right, text
    return out


def render_code_line(frags, base_left: int, char_w) -> str:
    out = " " * max(0, round((frags[0]["left"] - base_left) / char_w[frags[0]["font"]]))
    prev_right = None
    for f in frags:
        if prev_right is not None:
            w = char_w[f["font"]]
            gap = f["left"] - prev_right
            out += " " * (max(1, round(gap / w)) if gap >= 0.7 * w else 0)
        out += f["text"]
        prev_right = f["left"] + f["width"]
    if out.lstrip().startswith("#"):
        for pattern, repl in COMMENT_SPACES:
            out = pattern.sub(repl, out)
    return out.rstrip()


def guess_lang(code: str) -> str:
    if re.search(r"^\s*irb", code, re.M):
        return "irb"
    if re.search(r"^\s*\$ ", code, re.M):
        return "bash"
    if "<%" in code:
        return "erb"
    if re.search(r"^\s*(SELECT|INSERT|UPDATE|CREATE TABLE|ALTER TABLE)\b", code, re.M | re.I):
        return "sql"
    if re.search(r"^\s*(def|class|module|end)\b|\bdo\b|^\s*#", code, re.M):
        return "ruby"
    if re.search(r"^\s*[a-z_]+:\s", code, re.M):
        return "yaml"
    return ""


def join_text(a: str, b: str) -> str:
    if re.search(r"[a-z]-$", a) and re.match(r"[a-z]", b):
        return a[:-1] + b  # 行末ハイフネーション
    if a and b and (CJK.match(a[-1]) and CJK.match(b[0]) or a[-1] in OPEN_BRACKET or b[0] in CLOSE_PUNCT):
        return a + b
    return a + " " + b


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


class Writer:
    """行を受け取り、段落・リスト・コード・見出しの Markdown ブロックに組み立てる。"""

    def __init__(self, outline_by_page):
        self.outline_by_page = outline_by_page
        self.blocks = []
        self.kind = None
        self.buf = []
        self.meta = {}
        self.last_center = None
        self.last_left = None
        self.last_page = None

    def flush(self):
        if self.kind == "code":
            code = "\n".join(self.buf)
            self.blocks.append(f"```{guess_lang(code)}\n{code}\n```")
        elif self.kind == "heading":
            text = " ".join(self.buf)
            level = self.outline_level(self.meta["page"], text) or (2 if self.meta["size"] >= 28 else 3)
            self.blocks.append("#" * level + " " + text)
        elif self.kind in ("para", "item"):
            self.blocks.append(self.buf[0])
        self.kind, self.buf, self.meta = None, [], {}

    def outline_level(self, page: int, text: str):
        key = norm(text)
        for p in (page - 1, page, page + 1):
            for level, title in self.outline_by_page.get(p, []):
                if norm(title) == key:
                    return level
        return None

    def feed_page(self, page: int, lines):
        code_frags = [f for l in lines if l["is_code"] for f in l["frags"]]
        base_left = min((f["left"] for f in code_frags), default=0)
        widths = defaultdict(list)
        for f in code_frags:
            if len(f["text"]) >= 3:
                widths[f["font"]].append(f["width"] / len(f["text"]))
        char_w = defaultdict(lambda: 9.0, {font: statistics.median(ws) for font, ws in widths.items()})
        for line in lines:
            self.feed_line(page, line, base_left, char_w)

    def feed_line(self, page, line, base_left, char_w):
        frags = line["frags"]
        center = line["center"]
        gap = center - self.last_center if self.last_page == page else None
        self.last_center, self.last_left, self.last_page, prev_left = center, line["left"], page, self.last_left

        if line["is_code"]:
            text = render_code_line(frags, base_left, char_w)
            if self.kind != "code":
                self.flush()
                self.kind = "code"
            elif gap is not None and gap > 1.7 * CODE_PITCH:
                self.buf.append("")
            self.buf.append(text)
            return

        all_bold = all(f["bold"] for f in frags)
        size = max(f["size"] for f in frags)
        text = render_inline(frags)
        if all_bold and size >= 40:
            return  # 章扉の大見出しはしおりから出す
        if all_bold and size >= 23:
            if self.kind == "heading" and self.meta["size"] == size and gap is not None and gap < 1.6 * BODY_PITCH:
                self.buf.append(text)
            else:
                self.flush()
                self.kind, self.buf, self.meta = "heading", [text], {"page": page, "size": size}
            return

        first = frags[0]["text"]
        bullet = BULLET.match(first) if len(frags) > 1 or len(first) > len(BULLET.match(first).group(0) if BULLET.match(first) else "") else None
        admonition = ADMONITION.match(first)
        if bullet:
            self.flush()
            self.kind = "item"
            mark = bullet.group(1)
            marker = "  - " if mark == "–" else ("- " if mark == "•" else f"{mark} ")
            self.buf = [marker + BULLET.sub("", text, count=1)]
        elif admonition:
            self.flush()
            self.kind = "para"
            self.buf = [f"**{admonition.group(1)}:** " + ADMONITION.sub("", text, count=1)]
        else:
            new_para = (
                self.kind not in ("para", "item")
                or (gap is not None and gap > 1.5 * BODY_PITCH)
                or (gap is not None and 64 <= line["left"] <= 73 and prev_left is not None and prev_left < 60)
                or (gap is None and self.buf and self.buf[0].rstrip()[-1:] in "。.:：")
            )
            if new_para:
                self.flush()
                self.kind = "para"
                self.buf = [text]
            else:
                self.buf[0] = join_text(self.buf[0], text)

    def result(self) -> str:
        self.flush()
        return "\n\n".join(self.blocks) + "\n"


def classify(lines):
    kept = []
    for line in lines:
        if line["center"] < HEADER_LIMIT or line["center"] > FOOTER_LIMIT:
            continue
        line["is_code"] = all(f["mono"] and f["height"] <= 20 for f in line["frags"])
        kept.append(line)
    return kept


def main(pdf: Path, out_dir: Path):
    outline = read_outline(pdf)
    chapters = [(t, p) for level, t, p in outline if level == 1 and t.startswith("第")]
    outline_by_page = defaultdict(list)
    for level, title, page in outline:
        outline_by_page[page].append((level, title))
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    total = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    pages = read_pages(pdf, chapters[0][1], total)
    out_dir.mkdir(parents=True, exist_ok=True)
    index = [
        "# Rails ガイド 8.1 (railsguides.jp) 章一覧",
        "",
        "出典: Ruby on Rails ガイド 2026-08-21 版 (YassLab 株式会社発行、原著 Ruby on Rails Community)。本文は CC BY-SA 4.0。",
        "`scripts/pdf_to_markdown.py` で PDF から変換した。PDF のページ番号は各章の見出しに併記する。",
        "既知の限界: PDF の表は罫線情報がないため、セルが 1 文につながって出る。図は出ない。",
        "",
    ]
    for i, (title, start) in enumerate(chapters):
        end = chapters[i + 1][1] - 1 if i + 1 < len(chapters) else total
        num = int(re.match(r"第(\d+)章", title).group(1))
        name = f"ch{num:02d}.md"
        writer = Writer(outline_by_page)
        writer.blocks.append(f"# {title}")
        for page in range(start, end + 1):
            writer.feed_page(page, classify(group_lines(pages.get(page, []))))
        (out_dir / name).write_text(writer.result(), encoding="utf-8")
        index.append(f"- [{title}]({name}) (PDF p.{start}-{end})")
        for level, t, p in outline:
            if level == 2 and start <= (p or 0) <= end:
                index.append(f"  - {t}")
        print(f"{name}\t{title}\t{start}-{end}", file=sys.stderr)
    (out_dir / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
