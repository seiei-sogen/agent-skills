---
name: pipe-multiple-issues
description: 複数の GitHub issue をまとめて扱うパイプライン。内容は未定義で、まだ使わない。
---

# 複数の issue をまとめて処理する

以下。
[引数]で与えられた、複数の要件定義書 = `reqs` 
と表記する。

まず、修正対象が、バックエンド側か、フロントエンド側か、あるいは両方かを判定する。
`pstack`の`how`や`why`などを使ってもよい。

対象のリポジトリに、`git wt` commandで、git worktreeを作成する。

その中で、作業をするが、後述する、`pipe-requirements-to-pr` で生成されたドキュメントは、対応する、`reqs` のディレクトリに格納する。

git worktreeを生成した後、その中で、`pipe-requirements-to-pr` スキルを使い、複数の要件定義書 = `reqs` を一度に2PR
ずつ作業する。（セッションの節約のため。）

また、フロントエンド、バックエンド、両方の対応が必要な、場合、レビューガイドなどに、別PRで（フロントエンド or バックエンド）側の対応が必要か明記する。
