---
name: git-upstream-sync-rebase
description: 作業ブランチを origin/develop 上へ rebase して競合を解消する。develop の変更を rebase で取り込む場合や、すでに競合で停止している rebase を再開する場合に使用する。競合したゴールデンファイルや生成ファイルは再生成する。
---

<!-- https://github.com/wado-lang/wado/blob/develop/.claude/skills/git-upstream-sync/SKILL.md -->

# 概要

作業ブランチのコミットを `origin/develop` 上に積み直し、途中で発生する競合を解消して rebase を完了する。
作業ブランチをチェックアウトした状態で `git rebase origin/develop` を実行する方向を扱う。

## 手順

### 1. rebase の進行状況と対象ブランチを確認する

```sh
git status
git branch --show-current
git rev-parse --git-path rebase-merge
git rev-parse --git-path rebase-apply
```

`git status` と、上記で得たパスにある rebase 管理情報から、次のどちらかに進む。

- rebase が進行中なら、管理情報の `head-name` と `onto` で元の作業ブランチと rebase 先を確認する。対象の作業であることを確認して手順3へ進む。rebase 中の detached HEAD や競合による変更は正常な状態として扱い、新しい rebase を開始しない。
- rebase が進行中でなければ、現在のブランチが作業対象であり、未コミット変更がないことを確認して手順2へ進む。detached HEAD、`develop` 自体、別の作業ブランチ、または merge など別の操作が進行中なら停止して状況を報告する。未コミット変更は既存の指示に従って扱い、指示がなければ保持してユーザーに処理方法を確認する。

進行中の rebase の対象を確認できない場合は、状態を保持してユーザーに確認する。

### 2. develop をフェッチし、rebase を開始する

開始前の作業ブランチ名と `git rev-parse HEAD` のコミット ID を記録する。

```sh
git fetch origin develop
```

フェッチに失敗した場合は処理を止め、古い `origin/develop` を使って rebase しない。
フェッチに成功した場合だけ、次を実行する。

```sh
git -c merge.conflictstyle=zdiff3 rebase origin/develop
```

`zdiff3` は、競合マーカーに共通の元内容を表示しつつ、不要な重複を減らす。

- rebase が完了した場合は、手順5へ進む。
- rebase が停止した場合は、次のコマンドで未解消ファイルを確認する。

  ```sh
  git diff --name-only --diff-filter=U
  ```

  出力がある場合は、手順3へ進む。
  出力がない場合は `git status` とエラーを確認する。空コミット、編集待ち、フック失敗などを競合と決めつけず、停止理由に応じて対処する。

### 3. 現在のコミットの競合を解消する

```sh
git diff --name-only --diff-filter=U
git rebase --show-current-patch
```

各ファイルについて、適用中のコミットの意図、競合の両側、共通の元内容を確認して統合する。
rebase 中の `ours` は `origin/develop` と再適用済みコミットの側、`theirs` は現在再適用している作業ブランチのコミットの側を指す。
`ours` を作業ブランチ全体と考えて一括採用しない。

ゴールデンファイルや生成ファイルは、生成元の競合を先に解消し、後述の「生成ファイル」に従って再生成する。
解消したファイルだけを `git add -- <path>` でステージする。削除を採用する場合は `git rm -- <path>` を使う。

### 4. rebase を続行し、競合が出るたびに繰り返す

未解消ファイルがなく、解消対象に競合マーカーが残っていないこと、ステージした差分が意図どおりであることを確認する。

```sh
git diff --name-only --diff-filter=U
git diff --cached --check
git diff --cached
git -c merge.conflictstyle=zdiff3 rebase --continue
```

次のコミットで競合したら、手順3と手順4を繰り返す。
解消結果は `rebase --continue` によって再適用中のコミットへ反映する。競合マーカーを含むコミットや、競合解消専用のコミットを別途作成しない。
`rebase --skip` は、そのコミットの変更がすでに取り込まれているなど、スキップしても必要な変更を失わないと確認できた場合に限る。
フックなどが失敗した場合は原因を調べ、検証を無効化して進めない。対処できなければ rebase の状態を保持し、停止理由を報告する。

### 5. 簡易確認を実行する

リポジトリで定められたテストと、解消箇所に必要な確認を実行する。`mise run test` が用意されている場合はそれを使う。
テストが失敗した場合は同期完了とせず、原因を報告する。
テスト後に作業ツリーを確認する。

```sh
git status
git branch --show-current
```

rebase が終了し、元の作業ブランチに戻っていることを確認する。
テストが成功し、作業ツリーに未処理の変更がなければ完了とする。解消した競合と確認結果を報告する。
push は依頼に含まれる場合だけ実行する。rebase 後の公開済みブランチを更新する場合は、リモートの変更を確認して `--force-with-lease` を使う。

## 生成ファイル

- ゴールデンファイルまたは生成ファイルで競合が発生した場合は、必ず再生成する。
  リポジトリ既存のジェネレーターを再実行し、出力をステージして `rebase --continue` で再適用中のコミットへ含める。
  競合マーカーを手作業で解消しない。
  競合したファイルをスキップしたり、`on-task-done` や CI に先送りしたりしない。
- 競合がない場合は、タスクの明示的な指示に従って再生成の要否を判断する。
  再生成が常に必要とは限らない。
  「常に再生成する」「CI が処理する」といった一般的な方針を、依頼内容より優先してはならない。
- 生成結果を黙って破棄してはならない。
  作業ツリーをクリーンにしたり、フックの警告を消したりする目的で `git restore` を実行しない。
  rebase 中の解消に必要な生成結果は再適用中のコミットへ含める。完了後に残った生成結果は既存の指示に従って扱い、指示がなければユーザーに処理方法を確認する。
