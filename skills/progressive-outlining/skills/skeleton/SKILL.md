---
name: skeleton
description: Progressive Outlining の第3段階。アウトラインと批評を型定義・関数シグネチャ・テスト名に落とす。本体は未実装のまま、型検査だけ通す。
disable-model-invocation: true
argument-hint: "[slug]"
arguments: [slug]
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/po-stage.sh *)
---

!`${CLAUDE_PLUGIN_ROOT}/scripts/po-stage.sh skeleton ${CLAUDE_PROJECT_DIR}`

# /po:skeleton — 型とシグネチャに落とす

対象: `docs/po/$slug/`（全ファイルを読む。最新の批評に未対処の指摘があれば、まずそれを私に見せ、アウトラインに反映してから進む）

## 書くもの

- アウトラインのディレクトリ構成どおりにファイルを作る
- 型定義（ドメインの型、入出力の型、エラー型）
- 各モジュールの公開関数のシグネチャ。本体は言語の未実装慣用句（Rust: `todo!()` / TS: `throw new Error("not implemented")` 等）
- テスト: 名前と Arrange だけ。Act / Assert は書かない。`#[ignore]` / `it.todo` で無効化
- doc コメントで「何をするか」を1行。「どうやるか」は書かない

## 書かないもの

- 関数本体。分岐・ループ・I/O が1行でも入ったら書きすぎ
- シグネチャの整合に必要な最小限を超えるコード
- アウトラインに無い公開関数・モジュール（必要なら止めて相談）

## 検証

- 型検査を通す（`cargo check` / `tsc --noEmit` / プロジェクトの該当コマンド）。通らない間はシグネチャを直す
- 通ったら `docs/po/$slug/03-skeleton.md` に、シグネチャに現れない設計判断（エラー処理方針、境界を跨ぐデータの所有権、各テストの意図）を書く

## 終わり方

型検査の結果と、書いてみてアウトラインから変えた点を私に報告する。
私が満足したら `/po:critique $slug`（スケルトンの批評）か `/po:implement $slug` を提案する。
