---
name: frontend-impl-and-review
description: フロントエンド実装後に規約レビュー・自動修正・報告を一気通貫で行う
argument-hint: <task description>
user-invocable: true
---

# Frontend 実装 & レビュー

フロントエンドの実装を行い、完了後に `docs/review/frontend.md` に基づくセルフレビューを実施する。
直接影響の違反は修正し、間接的・判断が難しい違反は報告文書として保存する。

---

## 前提: ブランチ名からチケット ID を抽出

`git branch --show-current` を実行し、ブランチ名から `PFM-\d+` を抽出する。
以降、このチケット ID を `$TICKET_ID` として使用する。

抽出できない場合はユーザーに確認する。

---

## Phase 1 — 実装

`$ARGUMENTS` で指定されたタスクを実装する。

実装時は以下のスキルの規約に従うこと:
- `/frontend-component`, `/frontend-hook`, `/frontend-lib`, `/frontend-page`, `/frontend-util`（新規ファイル作成時）
- `docs/conventions/frontend-*.md`（既存ファイル編集時）

実装が完了したら Phase 2 に進む。

---

## Phase 2 — 機械チェック & 自動修正

`frontend/` ディレクトリで以下を **順番に** 実行する。

1. `pnpm check:fix` — Biome format + lint（自動修正）
2. `pnpm knip --fix --no-exit-code` — 未使用 export / import の自動削除
3. `pnpm tsgo` — 型チェック

- 自動修正で変更されたファイルがあれば記録する
- **エラーが残った場合はエラーを修正してから再実行する**
- 全パスしたら Phase 3 に進む

---

## Phase 3 — Agent レビュー

### 対象スコープ

`git diff --name-only -- frontend/` で **未コミットの変更ファイル一覧** を取得する（今回の実装で変更したファイルのみ）。

### レビュー実行

3 つのロール（Frontend Expert / Software Engineer / Design Engineer）を Agent として **並列スポーン** する。

各 Agent には以下を含める:

1. `docs/review/frontend.md` とそこからリンクされた **すべての規約ファイル** を Read する
2. 対象スコープ内の **全ファイルの全内容** を読み込む
3. チェックリストに沿って違反を検出し、以下の形式で報告する:
   - **ファイルパス:行番号** / **違反している規約** / **問題の説明** / **修正案** / **直接影響かどうか**

「直接影響」の判定基準:
- **直接影響**: 今回の diff で追加・変更した行、またはその変更が直接的に引き起こした問題
- **間接影響**: 変更ファイル内だが今回の diff に含まれない既存コードの問題、または判断が難しいもの

#### ロール別の重点観点

**Frontend Expert**: コンポーネント分割、Container/Presentational、App Router/RSC、hooks ルール、状態管理、パフォーマンス、型安全性

**Software Engineer**: 可読性・保守性、DRY/SOLID、エラーハンドリング、ロジックの正確性、バックエンド仕様との整合、セキュリティ

**Design Engineer**: UI/インタラクション一貫性、デザインシステム活用、スタイリング規約、アクセシビリティ、UX ライティング

---

## Phase 4 — 振り分け & 対応

Agent レビュー結果を統合・重複排除し、各指摘を以下の 2 カテゴリに振り分ける。

### A. 直接影響 → 修正する

今回の変更が直接的に引き起こした規約違反を修正する。

修正後、Phase 2（機械チェック）を再実行して問題がないことを確認する。

### B. 間接影響・判断が難しい → 報告文書を保存する

以下のパスに Markdown ファイルとして保存する:

```
docs/spec/PFM-{$TICKET_ID}-*/PFM-{$TICKET_ID}-review-{連番}.md
```

#### ファイルパスの決定手順

1. `docs/spec/` 配下で `PFM-{$TICKET_ID}-*` に一致するディレクトリを探す
2. そのディレクトリ内で `*-review-*.md` に一致するファイルの最大連番を取得する
3. 最大連番 + 1 で新しいファイルを作成する（既存ファイルは上書きしない）

例:
- 既存: `docs/spec/PFM-164-fr-file-unique-by-building-month/PFM-164-review-01.md`
- 新規: `docs/spec/PFM-164-fr-file-unique-by-building-month/PFM-164-review-02.md`

ディレクトリが見つからない場合はユーザーに確認する。

#### 報告文書のフォーマット

```markdown
# PFM-{$TICKET_ID} フロントエンドレビュー報告

ブランチ: `{ブランチ名}`
日付: {YYYY-MM-DD}

## 概要

{実装内容の1行サマリー}

## 間接影響・要検討の指摘

### {指摘番号}. {指摘タイトル}

- **ファイル**: `{パス}:{行番号}`
- **違反規約**: {規約名}
- **問題**: {説明}
- **修正案**: {提案}
- **指摘元**: {ロール名}

## サマリー

- 直接影響（修正済み）: N 件
- 間接影響（本報告）: N 件
```

---

## Phase 5 — 最終確認

Phase 2 の機械チェックを最終実行し、すべてパスすることを確認する。

以下を報告して完了:
- 実装内容のサマリー
- 直接影響で修正した件数と内容
- 間接影響の報告文書のパス（作成した場合）
