---
name: pr-description
description: git diff と commit 履歴から PR タイトルと本文を自動生成する
argument-hint: [--draft]
---

# PR Description 生成

git の差分とコミット履歴を分析し、構造化された PR タイトルと本文を日本語で生成する。

入力: $ARGUMENTS

## Step 1: 情報収集

以下の git コマンドを **並列で** 実行し、情報を収集する。

1. `git branch --show-current` — 現在のブランチ名を取得
2. `git log main..HEAD --oneline` — コミット一覧を取得
3. `git diff main...HEAD --stat` — ファイル変更サマリーを取得
4. `git diff main...HEAD` — 全差分を取得

差分が空の場合は **「main との差分がありません」** と報告して終了する。

## Step 2: 分析

収集した情報から以下を抽出・判定する。

### Jira チケット

ブランチ名のパス区切りから `PFM-\d+` にマッチするセグメントを探す。

- 例: `feat/PFM-150/sort_floors_descending` → `PFM-150`
- 見つからない場合はプレースホルダーとする

### 変更タイプ（PR タイトル用）

ブランチ名の先頭セグメント（prefix）から type を決定する。

| prefix | type |
|--------|------|
| feat | feat |
| fix | fix |
| hotfix | fix |
| chore | chore |
| doc / docs | docs |
| refactor | refactor |
| test | test |

prefix が上記に該当しない場合は、コミットメッセージの type 分布から最も多いものを採用する。

### カテゴリ分類

`--stat` の出力からファイルパスを分類する。

| パス | カテゴリ |
|------|---------|
| `backend/**` | バックエンド |
| `frontend/**` | フロントエンド |
| `sql/**` | データベース |
| `infra/**` | インフラ |
| その他 | CI / 設定 |

### 影響範囲の検出

diff の内容から以下を特定する。

- **画面**: `frontend/app/` 配下のルートセグメントから影響する画面を特定
- **API**: `backend/graphql/` 配下の変更から影響する GraphQL エンドポイント / Mutation を特定
- **テーブル**: `sql/` 配下の変更から影響するデータベーステーブルを特定

### UI 変更の有無

`frontend/` 配下で `.tsx` または `.module.css` ファイルの変更があれば UI 変更ありとする。

## Step 3: 出力生成

### PR タイトル

形式: `<type>: <日本語の説明>`

- コミット履歴と diff から、変更の目的を簡潔に日本語で記述する
- 50文字以内を目安とする

### PR 本文

以下のテンプレートに従い、分析結果を埋めて出力する。

```markdown
## Summary
<!-- なぜこの変更が必要か（課題・動機）を1文で書き、その後に何をしたかを箇条書き -->
- 変更の要点を箇条書きで簡潔に（1〜3項目）

## 変更内容
- 変更点を機能・目的の単位で記述（ファイル単位ではなく）
- カテゴリ（バックエンド / フロントエンド / DB / インフラ）が複数ある場合のみサブセクション化

## Test plan
- [ ] レビュアーが確認すべき動作チェック項目
```

## セクションの出し分けルール

| 条件 | 対応 |
|------|------|
| Jira チケット検出 | Summary の先頭に `Jira: [PFM-xxx](https://estie.atlassian.net/browse/PFM-xxx)` を追加 |
| UI 変更あり | Test plan の末尾に `- [ ] スクリーンショット添付` を追加 |
| マイグレーション等が必要 | `## 備考` セクションを追加 |

## `--draft` フラグ

`$ARGUMENTS` に `--draft` が含まれる場合:

- PR タイトルは出力しない
- 自動生成した各セクションの末尾に `<!-- AI generated: review and edit -->` マーカーを付与する

## 出力方法

生成した PR タイトルと本文を **コードブロック** で表示する。
PR の作成自体は行わない（`/create-pr` に任せる）。

## 記述ルール

- **変更内容はファイル単位ではなく、機能・目的の単位で記述する**
  - NG: `backend/graphql/building.rs を変更`
  - OK: `建物一覧の取得クエリにフロア降順ソートを追加`
- 概要・背景は diff とコミットメッセージから推測して記述する
- 推測に自信がない箇所には `<!-- 要確認 -->` を付記する