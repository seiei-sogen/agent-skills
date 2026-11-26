---
name: git-repo-update
description: 日報 nippo.adoc に載っている開いた PR のうちワークツリーがないものを git-wt で作り直し、AICROSS 配下の develop・main を fish の gp で pull し、git-wt のワークツリーを fish の gur で PR の base へ rebase して、競合を解消する。
disable-model-invocation: true
---

# git-repo-update

`~/develop/github.com/AICROSS/` 配下の各リポジトリを最新にする。
先に、日報（`~/develop/github.com.sogen/seiei-sogen/enterprise-agent-ssot/enterprises/ai-cross-memo/nippo/nippo.adoc`）に載っている PR のうち、開いているのにワークツリーがないもの（自動の後片付けで消えたものなど）を git-wt で作る。
**元のワークツリー**（`git worktree list` の先頭にある develop・main・master）は `gp` で pull し、git-wt で作った**ワークツリー**は `gur` で PR の base へ rebase する。
`gp` と `gur` はユーザーの fish 関数で、スクリプトは `fish -c` でそのまま呼ぶ。

## 1. 一括で更新する

このスキルの `scripts/git-repo-update.sh` を実行する。数分かかるので、コマンドの待ち時間の上限を10分に延ばす。

```sh
bash "<このスキルのディレクトリ>/scripts/git-repo-update.sh" [root] [nippo]
```

標準エラーには `git wt`・`gp`・`gur` の出力が、標準出力の最後には結果の TSV（`RESULT KIND BRANCH PATH NOTE`）が出る。
終了コード2は root のディレクトリがないか、fish の `gp`・`gur` か `git-wt` を読み込めなかったことを示すので、そこで止めて報告する。

KIND が `create` の行は、日報の PR からワークツリーを作った結果で、作ったワークツリーは続けて `gur` で rebase される（KIND が `worktree` の行）。
ワークツリーは各リポジトリの `wt.basedir`（`../.worktrees`）に `<リポジトリ名>-<ブランチ名>` の名前で作る。
ローカルに残っていたブランチが origin より古ければ origin まで進めてから作り、origin と分岐していれば作らずに SKIP にする。
ディレクトリだけ消えて登録が残ったワークツリーは、作る前に `git worktree prune` で片付ける。

| RESULT | 状態 | 次にやること |
| --- | --- | --- |
| OK | 更新できた。NOTE に `force-with-lease` があれば、ローカルで rebase して origin と分岐している | 手順3で報告する |
| CONFLICT | rebase が競合で止まった | 手順2で解消する |
| FAIL | `git wt`・`gp`・`gur` が失敗した（fast-forward できない、gh の認証エラーなど） | 標準エラーから原因を読み、手順3で報告する |
| SKIP | 更新の対象外。理由は NOTE にある | そのままにして、手順3で NOTE を報告する。NOTE が「分岐している」の行は、どちらのコミットを残すかをユーザーに聞く |

## 2. CONFLICT の行で競合を解消する

CONFLICT の行ごとに PATH へ移動し、[`git-upstream-sync-rebase`](../git-upstream-sync-rebase/SKILL.md) に従って、止まっている rebase を最後まで進める。

- rebase は `gur` が始めているので、`git-upstream-sync-rebase` の手順1にある「rebase が進行中なら」の分岐から進める。取り込み先は PR の base で、`origin/develop` とは限らない。
- rebase が終わっていて未解消のファイルだけが残る場合は、`gur` が退避した未コミットの変更を戻すときに競合している（`Applying autostash resulted in conflicts`）。退避した変更は `git stash list` に残るので、作業ツリーの競合を解消し、stash は残したまま報告する。

## 3. 報告する

結果の表に加えて、次を報告する。

- 作ったワークツリー（KIND が `create` の OK の行）
- `git push --force-with-lease` が必要なブランチ（NOTE にそう書かれた OK の行と、手順2で解消した行）
- FAIL と SKIP の理由、解消できなかった競合

push は、ユーザーに頼まれたときだけ行う。リモートの先端を確認し、`git push --force-with-lease=<branch>:<確認した先端>` で送る。

スクリプトを変えたら、`bash "<このスキルのディレクトリ>/scripts/git-repo-update.test.sh"` が `PASS` で終わることを確かめる。
