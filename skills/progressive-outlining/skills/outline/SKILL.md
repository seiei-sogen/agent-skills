---
name: outline
description: Progressive Outlining の第1段階。機能の粗い構造（EARS 要件・スコープ・ディレクトリ構成・モジュール境界）をユーザーと議論しながら docs/progressive-outlining/<slug>/01-outline.md に作る。コードは書かない。
disable-model-invocation: true
argument-hint: "[slug]"
arguments: [slug]
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/po-stage.sh *)
---

!`${CLAUDE_PLUGIN_ROOT}/scripts/po-stage.sh outline ${CLAUDE_PROJECT_DIR}`

# /po:outline — 粗い構造を作る

対象 slug: `$slug`（空ならまず私に聞く。kebab-case）
成果物: `docs/progressive-outlining/$slug/01-outline.md`

## 進め方

1. `docs/progressive-outlining/$slug/` が既にあれば全ファイルを読み、前回の続きから始める。批評ファイルがあれば、未対処の指摘を先に列挙する。
2. 目的・非スコープ・制約・受け入れ条件を私に質問して確定させる。一度に聞く質問は3つまで。
3. 既存コードの関連箇所を Explore サブエージェントで調べ、影響範囲をファイル単位で列挙する。
4. 設計判断で迷う点は2〜3案を並べ、長所・短所を書き、私に選ばせる。自分で決めない。
5. 下の構成で `01-outline.md` を書く／更新する。

## 01-outline.md の構成

- 目的（1段落）
- 非スコープ
- 要件（EARS 形式: `WHEN … / WHILE … / IF … , THE SYSTEM SHALL …`）
- 制約（既存 API・性能・互換性）
- ディレクトリ構成案（ツリー。各エントリに責務を1行添える）
- モジュール境界と依存の向き（`A → B` の一覧。逆流がないことを明示）
- 外部依存（追加するクレート／パッケージと理由）
- 未決事項（私の回答待ちの問い）

## 禁止

- `docs/progressive-outlining/` 以外への書き込み（フックでブロックされる）
- 関数本体を書くこと。シグネチャの例示も境界の説明に必要な最小限に留める
- 私が「次へ」「批評して」などと言う前に次の段階へ進むこと

## 終わり方

毎ターン、未決事項を列挙して私の判断を仰ぐ。決まったら `01-outline.md` を更新する。
私が満足したら `/po:critique $slug` を提案する。
