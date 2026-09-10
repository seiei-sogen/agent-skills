---
name: critique
description: Progressive Outlining の批評段階。docs/po/<slug>/ のアウトラインまたはスケルトンを、会話履歴を持たない別コンテキストで rubric.md に沿って批評し、docs/po/<slug>/NN-critique.md に書く。
disable-model-invocation: true
argument-hint: "[slug]"
arguments: [slug]
context: fork
agent: po:critic
background: false
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/po-stage.sh *)
---

!`${CLAUDE_PLUGIN_ROOT}/scripts/po-stage.sh critique ${CLAUDE_PROJECT_DIR}`

# /po:critique — 別コンテキストで批評する

対象: `docs/po/$slug/`
slug が空なら、上の一覧から推測せずに「slug を指定してください」とだけ返して終了する。

採点基準: `${CLAUDE_SKILL_DIR}/rubric.md` を最初に読む。

## 手順

1. `docs/po/$slug/` の全ファイルを番号順に読む。批評対象は最新の成果物（`03-skeleton.md` があればスケルトン、なければ `01-outline.md`）。
2. 対象がコードやファイルに言及していれば、該当ファイルを実際に読んで照合する。存在しないファイルを前提にした批評はしない。
3. rubric の各項目について、判定（OK / 要検討 / NG）・根拠（該当箇所の引用か行参照）・修正案を書く。
4. rubric 外でも、実装に入ってから発覚すると手戻りが大きい問題は「その他」に書く。
5. 結果を `docs/po/$slug/NN-critique.md` に書く（NN は既存ファイルの最大番号 + 1、2桁ゼロ埋め）。
6. 会話には冒頭の「要約」だけを返す。

## 出力ファイルの構成

- 要約（最重要の指摘を3つ以内）
- rubric 項目ごとの判定・根拠・修正案
- その他
- 前回の批評からの継続事項（あれば）

## 態度

- 中立。良い点は書かない。作者を励まさない。
- 修正案は「案」。決定はしない。案が複数あるなら並べる。
- 前回の批評ファイルがあれば読み、対処済みの指摘は繰り返さない。未対処なら「前回から継続」と明示する。
- コード・テスト・スケルトンは書かない。`docs/po/` 以外は変更しない。
