---
name: git-repo-update
description: 日報（nippo.md か nippo.adoc）に載っている開いた PR のうちワークツリーがないものを git-wt で作り直し、AICROSS 配下の develop・main を fish の gp で pull し、git-wt のワークツリーに fish の gum と同じ手順で PR の base をマージして、競合を解消する。
disable-model-invocation: true
---

# git-repo-update

`~/develop/github.com/AICROSS/` 配下の各リポジトリを最新にする。
先に、日報（`~/develop/github.com.sogen/seiei-sogen/enterprise-agent-ssot/enterprises/ai-cross-memo/nippo/nippo.md`、なければ `nippo.adoc`）に載っている PR のうち、開いているのにワークツリーがないもの（自動の後片付けで消えたものなど）を git-wt で作る。
**元のワークツリー**（`git worktree list` の先頭にある develop・main・master）は、ユーザーの fish 関数 `gp` で pull する。
git-wt で作った**ワークツリー**には、fish 関数 `gum`（`~/develop/github.com.sogen/seiei-sogen/linux-xdg-config-dotfiles/fish/conf.d/alias_git.fish`）と同じ手順で、PR の base（develop・main など）をマージする。

1. PR があれば、GitHub 側で base をマージして（`gh pr update-branch`）、`git pull --no-rebase --no-edit origin <ブランチ>` で手元に取り込む。
2. GitHub 側でマージできなければ（競合や PR なし）、`git fetch origin` のあと、手元で `git merge --no-edit origin/<base>` する。base は PR の base で、PR がなければ `origin/HEAD` の既定ブランチ。

`gum` と同じく `--autostash` は付けず、未コミットの変更があっても進める。マージが触るファイルと重なるときは git が止める。
スクリプトは、fish の定義がない環境でも動くよう、`gum` を呼ばずに同じ手順を bash で行う。`gum` との違いは次の3つ。

- 競合マーカーは、解消に使う `git-upstream-sync` と同じ `zdiff3` 形式で出す。
- PR がなく、`origin/HEAD` が未設定か、既定ブランチが元のブランチと違うとき（develop で開発し、main が既定のリポジトリなど）は、マージ先を決められないので SKIP にする。
- `git push` の案内は、標準出力の表の NOTE に書く。

rebase と違ってコミットの SHA が変わらないので、force push は要らない。

## 1. 一括で更新する

このスキルの `scripts/git-repo-update.sh` を実行する。数分かかるので、コマンドの待ち時間の上限を10分に延ばす。

```sh
bash "<このスキルのディレクトリ>/scripts/git-repo-update.sh" [root] [nippo]
```

標準エラーには `git wt`・`gp`・`gh`・`git pull`・`git merge` の出力が、標準出力の最後には結果の TSV（`RESULT KIND BRANCH PATH NOTE`）が出る。
終了コード2は root のディレクトリがないか、fish の `gp` か `git-wt` を読み込めなかったことを示すので、そこで止めて報告する。

KIND が `create` の行は、日報の PR からワークツリーを作った結果で、作ったワークツリーにも続けて base をマージする（KIND が `worktree` の行）。
ワークツリーは各リポジトリの `wt.basedir`（`../.worktrees`）に `<リポジトリ名>-<ブランチ名>` の名前で作る。
ローカルに残っていたブランチが origin より古ければ origin まで進めてから作り、origin と分岐していれば作らずに SKIP にする。
ディレクトリだけ消えて登録が残ったワークツリーは、作る前に `git worktree prune` で片付ける。

| RESULT | 状態 | 次にやること |
| --- | --- | --- |
| OK | 更新できた。NOTE に `git push が必要` があれば、手元でマージしたコミットが origin にまだない | 手順3で報告する |
| CONFLICT | マージが競合で止まった。NOTE の `merge origin/<…>` が取り込んだ元。未コミットの変更があれば、そのことも NOTE にある | 手順2で解消する |
| FAIL | `git wt`・`gp`・`git merge` が失敗した（fast-forward できない、gh の認証エラーなど） | 標準エラーから原因を読み、手順3で報告する |
| SKIP | 更新の対象外。理由は NOTE にある | そのままにして、手順3で NOTE を報告する。NOTE が「分岐している」の行は、どちらのコミットを残すかをユーザーに聞く |

## 2. CONFLICT の行で競合を解消する

CONFLICT の行ごとに PATH へ移動し、[`git-upstream-sync`](../git-upstream-sync/SKILL.md) に従って競合を解消する。

- マージはスクリプトが `zdiff3` 形式で始めて、競合で止めている。`git-upstream-sync` の手順2にある「マージコマンドが失敗した場合」から進め、フェッチとマージはやり直さない。
- 取り込んだ元は NOTE の `merge origin/<…>` で、`origin/develop` とは限らない（GitHub 側でマージした結果の取り込みで競合したときは `origin/<ブランチ名>`）。コミットメッセージの `origin/develop` も取り込んだ元に読み替える。
- NOTE に「未コミットの変更か未追跡のファイルがある」とある行では、手順3・4の `git add -A` が、元からあった変更までコミットに入れてしまう。`git-upstream-sync` の手順1と同じく、既存の変更を stash・破棄・コミットせず、ユーザーに処理方法を確認してから進める。
- 手順5の `mise run test` がないリポジトリでは、そのリポジトリのテストの手順を使う。

## 3. 報告する

結果の表に加えて、次を報告する。

- 作ったワークツリー（KIND が `create` の OK の行）
- `git push` が必要なブランチ（NOTE にそう書かれた OK の行と、手順2で解消した行）
- FAIL と SKIP の理由、解消できなかった競合

push は、ユーザーに頼まれたときだけ行う。マージなので、force ではない通常の `git push` で送れる。

スクリプトを変えたら、`bash "<このスキルのディレクトリ>/scripts/git-repo-update.test.sh"` が `PASS` で終わることを確かめる。
