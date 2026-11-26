---
name: nippo-and-repo-update
description: nippo-only-update で日報 nippo.adoc を Backlog と GitHub から更新し、続けて git-repo-update で日報の開いた PR のワークツリーを作り直して AICROSS 配下のリポジトリを更新する。日報とリポジトリをまとめて最新にしたいときに使う。
disable-model-invocation: true
---

# nippo-and-repo-update

日報を先に更新し、その日報に載った PR を使ってリポジトリを更新する。
git-repo-update は日報の PR からワークツリーを作るので、順番を逆にしない。

1. [`nippo-only-update`](../nippo-only-update/SKILL.md) の手順1・2を行う。終了コード2なら、ここで止めて報告する。終了コード1でも、取れた分は日報に書かれているので次へ進む。
2. [`git-repo-update`](../../git/git-repo-update/SKILL.md) の手順1・2を行う。日報のパスを変えたときは、スクリプトの第2引数に同じパスを渡す。
3. 2つのスキルの報告の手順を合わせて、1つの報告にする。日報で足した課題と PR、作ったワークツリー、`git push --force-with-lease` が必要なブランチ、失敗と SKIP の理由を伝える。
