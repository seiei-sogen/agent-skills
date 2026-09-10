---
name: implement
description: Progressive Outlining の最終段階。docs/progressive-outlining/<slug>/ のスケルトンの本体を1関数ずつ埋め、テストを有効化して通す。
disable-model-invocation: true
argument-hint: "[slug]"
arguments: [slug]
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/po-stage.sh *)
---

!`${CLAUDE_PLUGIN_ROOT}/scripts/po-stage.sh implement ${CLAUDE_PROJECT_DIR}`

# /po:implement — 本体を埋める

対象: `docs/progressive-outlining/$slug/`（全ファイルを読む。特に `03-skeleton.md` と最新の critique）

## 進め方

1. 未実装の関数を依存の下流から順に並べる（依存されるものを先に）
2. 1関数ずつ: 本体を書く → 対応するテストを有効化し Act / Assert を書く → 通す → 次へ
3. シグネチャや型を変えたくなったら、変えずに止めて私に相談する。アウトラインに戻るかどうかは私が決める
4. 全部通ったら lint / format を実行し、`docs/progressive-outlining/$slug/04-implement-notes.md` に「スケルトンから変えた点」「残した TODO」を書く

## 禁止

- スケルトンに無い公開関数・モジュールを勝手に増やすこと
- 自作コードをモックしてテストを通すこと
- テストを削除・無効化したまま「通った」と報告すること

## 終わり方

テスト結果と変更ファイル一覧を報告し、`/code-review` の実行を提案する。
