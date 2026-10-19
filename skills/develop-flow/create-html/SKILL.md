---
name: create-html
description: 説明資料・レビュー・レポートを、図と細かなシンタックスハイライト付きの単体HTMLにする。HTMLで説明してほしいときや、他のスキルがHTML出力を必要とするときに使う。
---

# HTML資料を作る

呼び出し元から内容、読者、出力先を受け取り、ブラウザで直接開けるHTMLを作る。説明の方針とファイル名の指定は呼び出し元に従う。

## HTMLを書く

一時ファイルに `<!doctype html>`、`html`、`head`、`body` を持つHTMLを書く。日本語なら `lang="ja"` を付け、UTF-8とviewportを指定する。
CSSはHTML内に埋め込み、図はインラインSVG、画像はdata URIにする。外部のCSS、JavaScript、Webフォントを必要としない形にする。
図の背景と文字を別々に指定し、白地に白文字などを避ける。狭い画面では本文を折り返し、長いコードはコード枠の中だけで横スクロールさせる。

コードブロックは、コードをHTMLのテキストとしてエスケープして次の形にする。

```html
<pre><code class="language-typescript">const count: number = 42;</code></pre>
```

`typescript`、`tsx`、`ruby`、`python`、`sql`、`bash` など、実際のコードの言語を指定する。`ts`、`js`、`rb` のようなShikiの別名も使える。
ログや疑似コードは明示的に `language-text` にする。文中の短い `<code>` はそのままでよい。
コード内に手作業で色付け用のspanや行番号を混ぜない。行番号や説明ラベルはコードの外に置く。

## コードを色付けして出力する

Node.js 20以降とnpmを使う。実行時のカレントディレクトリではなく、このSKILL.mdがあるディレクトリを `<skill-root>` とする。
読み取り専用のスキル配置でも動くように、実行に必要なファイルを一時ディレクトリへコピーする。

```bash
html_runner=$(mktemp -d)
cp <skill-root>/package.json <skill-root>/package-lock.json "$html_runner/"
cp -R <skill-root>/scripts "$html_runner/"
npm ci --prefix "$html_runner" --ignore-scripts --no-audit --no-fund
node "$html_runner/scripts/highlight.mjs" /absolute/path/draft.html /absolute/path/output.html
```

依存パッケージがキャッシュにない場合、準備時にネットワーク接続が必要になる。完成HTMLを開くときには不要。
入力と出力は別のパスにする。出力先が既に存在すると処理は失敗するので、別名にするか、再生成してよい既存出力かを確認して扱う。

同梱の [highlight.mjs](scripts/highlight.mjs) は `pre > code` をShikiのTextMate文法と `dark-plus` テーマで色付けする。型、関数、変数、文字列、数値、コメントなどを文法に応じて区別し、色をHTMLへ埋め込む。
Tree-sitterや言語サーバーによる意味解析ではない。言語や文脈によって同じ色になる構文もある。
色付け後の `.shiki` の背景色とトークンの文字色を、ページ共通CSSで上書きしない。

言語指定の欠落や未対応の言語名はエラーになる。言語を訂正して再実行する。色付けに失敗したコードを無言でプレーンテキストに変えない。

## 完成HTMLを確認する

生成したHTMLをブラウザで開き、コードの型・関数・文字列などの色分けと、本文・図の読みやすさを確認する。
狭い画面でページ全体が横にはみ出さないことも確認する。
元のコードと表示されたテキストを照合する。HTMLの改行はLFに正規化される。
生成処理の検証には `npm test --prefix "$html_runner"` を使う。

完成HTMLのパスと確認結果を報告する。
