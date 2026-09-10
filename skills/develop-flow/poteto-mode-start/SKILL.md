---
name: poteto-mode-start
description: 現在の開発タスクを、実行中の Claude Code または Codex に合う方法で pstack の poteto-mode に渡す。慎重な設計、実装、実アプリでの検証、PR 作成が必要なタスクで使う。
---

# poteto-mode でタスクを始める

このスキルと一緒に渡されたユーザーの依頼全体を、poteto-mode で実行する対象タスクとして扱う。

実行中のホストを確認し、open-pstack 本体の `pstack:poteto-mode` を次の方法で呼び出す。

- Claude Code では `/pstack:poteto-mode <ユーザーの依頼>` を実行する。
- Codex では `pstack:poteto-mode` スキルを使い、ユーザーの依頼をそのまま対象タスクにする。

以後の作業手順は、呼び出した `pstack:poteto-mode` を唯一のソースとして完了まで従う。

対象タスクが渡されていない場合は、何を進めるかをユーザーに確認する。

`pstack:poteto-mode` が見つからない場合は、open-pstack が未導入または未読み込みであることと、導入元の `https://github.com/ericlitman/open-pstack` を伝える。
