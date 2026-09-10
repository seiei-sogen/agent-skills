---
name: skeleton-03
description: Progressive Outlining の第3段階。ユーザーが skeleton-03 を明示した場合に、アウトラインと批評を型定義・関数シグネチャ・テスト名へ落とす。
---

# skeleton-03 で型とシグネチャに落とす

## 段階を開始する

呼び出し時に指定された値を `<slug>` とする。
slug が空なら、slug を確認してから進める。
最初にリポジトリルートの `docs/progressive-outlining/.stage` へ `skeleton` と書く。

対象: `docs/progressive-outlining/<slug>/`（全ファイルを読む。最新の批評に未対処の指摘があれば、まずそれを私に見せ、アウトラインに反映してから進む）

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
- 通ったら `docs/progressive-outlining/<slug>/03-skeleton.md` に、シグネチャに現れない設計判断（エラー処理方針、境界を跨ぐデータの所有権、各テストの意図）を書く

## 終わり方

型検査の結果と、書いてみてアウトラインから変えた点を私に報告する。
私が満足したら、`critique-02 <slug>` でスケルトンを批評するか、`implement-04 <slug>` へ進むことを提案する。
