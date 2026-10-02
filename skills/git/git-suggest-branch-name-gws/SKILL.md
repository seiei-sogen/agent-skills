---
name: git-suggest-branch-name-gws
description: issue 番号と変更内容から所定形式の Git ブランチ名を生成し、fish の gws でその名前のワークツリーを作成する。ユーザーが「ブランチ名を考えて、そのまま gws でワークツリーを作って」など、命名とワークツリー作成をまとめて依頼したときに使う。
---

# ブランチ名を生成して gws でワークツリーを作る

ブランチ名を1件確定し、その名前を引数に `gws` を実行する。
このスキルによる作成依頼には、`gws` が行う既定ブランチへの切り替えと更新も含む。
名前の提案だけを求められた場合は、[git-suggest-branch-name](../git-suggest-branch-name/SKILL.md) を使う。

## 1. ブランチ名を確定する

[git-suggest-branch-name](../git-suggest-branch-name/SKILL.md) を読み、入力確認、命名形式、Git の制約に従って第一候補を1件生成する。
不足情報への質問が必要な場合は、回答を受けて名前が確定するまで作成へ進まない。
既存スキルの出力手順の代わりに、以下の手順で作成まで行う。

対象リポジトリで `git check-ref-format --branch '<確定したブランチ名>'` を実行し、成功を確認する。

## 2. gws で作成する

`/home/agir_wsl/.config/fish/conf.d/alias_git.fish` の `gws` 定義を読み、現在の動作を確認する。
対象リポジトリで `git worktree list --porcelain` を実行し、作成前の状態を確認する。
同名ブランチのワークツリーが既にある場合は、そのパスを報告して終了する。

対象リポジトリを作業ディレクトリにして、次のコマンドの `<確定したブランチ名>` を置き換えて1回実行する。
ブランチ名は fish のコマンド文字列に埋め込まず、引数として渡す。

```bash
fish -c 'source /home/agir_wsl/.config/fish/conf.d/alias_git.fish; and gws "$argv[1]"' -- '<確定したブランチ名>'
```

`gws` は既定ブランチを更新して `git wt` で作成し、VS Code と Orca の更新処理も行う。
別途 `git switch -c` や `git worktree add` を重ねて実行しない。
fish、設定ファイル、`gws` の依存コマンドが利用できない場合は、原因を報告して終了する。

## 3. 作成結果を確認する

実行後は終了コードにかかわらず `git worktree list --porcelain` を確認する。
`branch refs/heads/<確定したブランチ名>` に対応する `worktree` のパスを取得する。
そのパスで `git -C '<ワークツリーのパス>' branch --show-current` を実行し、確定した名前と一致することを確認する。

成功した場合は、ブランチ名とワークツリーの絶対パスを簡潔に報告する。
失敗した場合は、エラーと実際の作成状態を報告して終了する。
作成後の連携処理だけが失敗した場合も、作成済みのパスを伝え、`gws` を再実行しない。
