---
name: sentence-linebreak
description: Add rendered per-sentence hard line breaks to Markdown and AsciiDoc prose. For Markdown, append HTML br tags at sentence ends. For AsciiDoc, append the hard line break marker at the end of each sentence line. Preserve code blocks, tables, front matter, and structural markup.
---

# Sentence Linebreak Skill

## 目的

Markdown または AsciiDoc の文章を、レンダー時に「一文ごとに改行」される形へ整える。

- Markdown: 文末に `<br>` を挿入する。
- AsciiDoc: 文末の行末に ` +`、つまり半角スペース + プラス記号を挿入する。

AsciiDoc の ` +` は行末に置かないと hard line break として効かないため、AsciiDoc では一文ごとにソース上でも改行する。

## 使うタイミング

ユーザーが次のような依頼をしたときに使う。

- Markdown の各文末に `<br>` を入れたい。
- AsciiDoc の各文末に ` +` を入れたい。
- レンダー後、一文ごとに改行される文書へ変換したい。
- `.md`, `.markdown`, `.adoc`, `.asciidoc` の既存ファイルを hard line break 付きにしたい。

## 基本方針

1. 対象形式を判断する。
   - `.md`, `.markdown` は Markdown。
   - `.adoc`, `.asciidoc`, `.asc` は AsciiDoc。
   - 拡張子が曖昧な場合は本文の記法、またはユーザーの明示指定を優先する。
2. prose paragraph だけを変換する。
3. コードブロック、表、front matter、リンク定義、属性行、見出し、構造用マークアップは壊さない。
4. すでに `<br>` または ` +` が入っている文末には重複して追加しない。
5. 日本語文末と英語文末の両方を扱う。

## 文末として扱う主な記号

通常は次を文末候補にする。

- 日本語: `。`, `！`, `？`
- 英語: `.`, `!`, `?`
- 閉じ括弧・閉じ引用符が続く場合は、それも文末に含める。
  - 例: `です。」`, `works.)`, `right?”`

英語のピリオドは誤判定しやすいので、次のようなものは原則として分割しない。

- 小数: `3.14`
- URL / ドメイン: `example.com`
- よくある略語: `e.g.`, `i.e.`, `Mr.`, `Dr.`, `etc.` など

## Markdown 変換ルール

Markdown では文末直後に `<br>` を入れる。

```markdown
これは一文目です。<br>
これは二文目です！<br>
これは三文目です？<br>
```

Markdown では `<br>` が inline hard break として働くため、同じソース行に複数文が残っていてもレンダー上は改行される。ただし、読みやすさのため、通常の段落では一文ごとにソース行も分けるのが望ましい。

変換例:

```markdown
これは一文目です。これは二文目です！
```

```markdown
これは一文目です。<br>
これは二文目です！<br>
```

### Markdown で変換しないもの

原則として次はそのまま保持する。

- fenced code block: <code>```</code>, <code>~~~</code>
- indented code block
- YAML/TOML front matter
- Markdown table
- ATX heading: `# Heading`
- link reference definition: `[id]: https://example.com`
- HTML block
- horizontal rule

## AsciiDoc 変換ルール

AsciiDoc では文末を一文ごとに物理行へ分け、その行末に ` +` を入れる。

```asciidoc
これは一文目です。 +
これは二文目です！ +
これは三文目です？ +
```

変換例:

```asciidoc
これは一文目です。これは二文目です！
```

```asciidoc
これは一文目です。 +
これは二文目です！ +
```

### AsciiDoc で変換しないもの

原則として次はそのまま保持する。

- source/listing/literal/example/open/pass-through block
  - `----`, `....`, `====`, `****`, `____`, `++++`, `--` などの delimiter で囲まれたブロック
- table block: `|===` と表の行
- document title / section title: `= Title`, `== Section`
- block attribute: `[source,python]`, `[cols="1,1"]`
- attribute entry: `:toc:`, `:sectnums:`
- block title: `.Title`
- include/image/link などの macro 行
- コメント行: `// comment`

## 箇条書きの扱い

箇条書きの構造は壊れやすいため、迷ったら自動変換せず、内容部分だけを手で調整する。

Markdown の箇条書きでは、同じ list item 内で `<br>` を使う。

```markdown
- 一文目です。<br>
  二文目です。<br>
```

AsciiDoc の箇条書きでは、` +` が行末に必要であることに注意し、レンダー結果を確認する。

```asciidoc
* 一文目です。 +
二文目です。 +
```

複雑な nested list では、変換後に必ずレンダー結果を確認する。

## 既存ファイルを変換するときの手順

補助スクリプト `scripts/sentence_linebreak.py` がある場合は使用できる。

```bash
# Markdown を変換して別ファイルへ出力
python scripts/sentence_linebreak.py input.md --output output.md

# AsciiDoc を変換して別ファイルへ出力
python scripts/sentence_linebreak.py input.adoc --output output.adoc

# 拡張子で判定せず明示指定
python scripts/sentence_linebreak.py input.txt --format markdown --output output.md
python scripts/sentence_linebreak.py input.txt --format asciidoc --output output.adoc

# 上書き。元ファイルは .bak として保存
python scripts/sentence_linebreak.py input.md --in-place --backup-suffix .bak
```

変換後は、少なくとも以下を確認する。

- コードブロックの中身が変わっていない。
- 表の区切りやセル内容が壊れていない。
- Markdown では文末に `<br>` が重複していない。
- AsciiDoc では ` +` が行末に置かれている。
- 箇条書きや引用のレンダー結果が崩れていない。

## 出力スタイル

ユーザーに変換結果を直接返す場合は、対象形式の fenced code block で返す。

Markdown の場合:

````markdown
```markdown
これは一文目です。<br>
これは二文目です。<br>
```
````

AsciiDoc の場合:

````markdown
```asciidoc
これは一文目です。 +
これは二文目です。 +
```
````

ファイルを作成・更新した場合は、変換済みファイルだけを渡す。バックアップや中間ファイルは、ユーザーが求めた場合のみ渡す。
