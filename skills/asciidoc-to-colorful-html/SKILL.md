---
name: asciidoc-to-colorful-html
description: Convert local AsciiDoc files into polished, colorful standalone HTML with the stylesheet embedded in the HTML. Use when asked to render, export, or share .adoc, .asciidoc, or .asc as a single styled HTML file. Do not use for PDF conversion or site-wide Antora builds.
---

# AsciiDocをカラフルな単体HTMLへ変換する

AsciiDocをAsciidoctorで変換し、同梱テーマを`<style>`へ埋め込んだHTMLを生成する。入力ファイルは変更しない。

## 前提を確認する

変換には次が必要である。

- Go 1.22以降
- `asciidoctor`コマンド

作業前に両方を利用できるか確認する。依存が見つからない場合は、欠けているコマンドと導入候補を報告する。ユーザーの承認なしにパッケージをインストールしない。

## 変換する

このスキルのディレクトリを`<skill-root>`として、同梱のGoツールを使う。

```bash
go run <skill-root>/scripts/main.go input.adoc
```

既定では入力と同じディレクトリに同名の`.html`を生成する。

```text
docs/guide.adoc -> docs/guide.html
```

保存先を指定するときは`-output`を使う。

```bash
go run <skill-root>/scripts/main.go -output build/guide.html docs/guide.adoc
```

既存HTMLは上書きしない。ユーザーが上書きを明示した場合、または既存出力がこの変換処理の再生成物だと確認できた場合だけ`-force`を付ける。

```bash
go run <skill-root>/scripts/main.go -force -output build/guide.html docs/guide.adoc
```

既定ではローカル画像もdata URIとしてHTMLへ埋め込む。画像を外部ファイルのまま参照する必要がある場合だけ`-no-data-uri`を使う。

## 出力の契約

生成HTMLは次を満たす。

- CSSが単一の`<style>`要素に埋め込まれている。
- 外部stylesheet、Webフォント、JavaScriptへ依存しない。
- Asciidoctorの見出し、目次、表、コード、引用、admonition、画像、脚注を読みやすく表示する。
- デスクトップとモバイルで横にはみ出さない。
- 印刷時は背景と影を抑え、本文を読みやすくする。
- キーボードフォーカスと十分な文字コントラストを保つ。

テーマは`custom.css`の青緑系パレットを基調に、単体HTML向けのページ背景、カード、admonition別カラー、レスポンシブ配置を加えたものである。外部の参考CSSは実行時に読み込まず、`scripts/theme.css`をGoの`go:embed`で同梱する。

## 検証する

変換後に次を確認する。

1. 出力HTMLが存在し、空でない。
2. `<style>`があり、`<link rel="stylesheet">`がない。
3. 文書タイトルと主要な見出しがHTMLに含まれる。
4. Asciidoctorが警告を出した場合、include、画像、xrefなどの欠落を確認する。
5. 表、コードブロック、admonition、長いURLを含む文書では、ブラウザ表示または同等のHTML検査を行う。

変換に失敗した場合は、壊れたHTMLを完成品として渡さない。Asciidoctorのエラー、対象パス、再開に必要な修正を報告する。

## 完了報告

生成したHTMLのパス、使用した入力、画像を埋め込んだか、警告の有無を簡潔に報告する。ユーザーが求めない限り、中間HTMLや抽出CSSは作成しない。
