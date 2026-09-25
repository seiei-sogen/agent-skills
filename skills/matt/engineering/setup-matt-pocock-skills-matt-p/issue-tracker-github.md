# 課題トラッカー: GitHub

このリポジトリの問題と仕様は GitHub のイシューとして存在します。すべての操作には `gh` CLI を使用してください。

## 慣習

- **問題を作成**: `gh issue create --title "..." --body "..."`。複数行の本文にはヒアドキュメントを使用してください。
- **課題を読む**: `gh issue view <number> --comments`、`jq`でコメントをフィルタリングし、ラベルも取得します。
- **問題をリスト**: 適切な`--label`および`--state`フィルターを使用して`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`。
- **問題についてコメントする**: `gh issue comment <number> --body "..."`
- **ラベルの適用/削除**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **クローズ**: `gh issue close <number> --comment "..."`

`git remote -v`からリポジトリを推測します； `gh`はクローン内で実行すると自動的にこれを行います。

## プルリクエストをトリアージのサーフェスとして扱う

**リクエストのサーフェスとしてのPR: いいえ。** _(このリポジトリが外部PRを機能要求として扱う場合は`yes`に設定； `/triage-matt-p`がこのフラグを読み込みます。)_

`yes`に設定すると、PRは課題と同じラベルや状態で処理され、`gh pr`に相当するものが使用されます：

- **PRを読む**：差分については`gh pr view <number> --comments`と`gh pr diff <number>`。
- **トリアージ用に外部PRを一覧表示**：`gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`、その後`CONTRIBUTOR`、`FIRST_TIME_CONTRIBUTOR`、または`NONE`のうち`authorAssociation`のみを保持（`OWNER`/`MEMBER`/`COLLABORATOR`は除外）。
- **コメント/ラベル付け/クローズ**：`gh pr comment`、`gh pr edit --add-label`/`--remove-label`、`gh pr close`。

GitHubはイシューとプルリクエストで番号空間を共有しているので、単なる`#42`は次のいずれかになる場合があります：`gh pr view 42`で解決し、`gh issue view 42`にフォールバックします。

## スキルが「課題トラッカーに公開する」と言うとき

GitHubのイシューを作成する。

## スキルが「関連するチケットを取得する」と言うとき

`gh issue view <number> --comments` を実行してください。

## 道案内操作

`/wayfinder-matt-p` によって使用されます。**マップ** は単一の課題で、**子** の課題がチケットとしてあります。

- **マップ**：`wayfinder:map`とラベル付けされた単一の問題で、ノート / これまでの決定 / フォグ本体を保持します。`gh issue create --label wayfinder:map`。
- **子チケット**：マップに紐づけられたGitHubのサブイシューとして発行（サブイシューエンドポイントの`gh api`）。サブイシューが有効でない場合は、マップ本文のタスクリストに子を追加し、子本文の先頭に`Part of #<map>`を記入します。ラベル：`wayfinder:<type>`（`research`/`prototype`/`grilling`/`task`）。チケットが引き受けられたら、そのチケットは担当開発者に割り当てられます。
- **ブロッキング**: GitHubの**ネイティブな課題依存関係**、正式でUI上に表示される表現です。`<blocker-db-id>`がブロッカーの数値**データベースID**（`gh api repos/<owner>/<repo>/issues/<n> --jq .id`、_`#number`や`node_id`ではありません）の場合、`gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`とのエッジを追加します。GitHubは`issue_dependencies_summary.blocked_by`（オープンブロッカーのみ、ライブゲート）を報告します。依存関係が利用できない場合、子課題本文の先頭に`Blocked by: #<n>, #<n>`行を使用します。すべてのブロッカーがクローズされたときにチケットはブロック解除されます。
- **フロンティアクエリ**: マップのオープンな子（`gh issue list --state open`、マップのサブ課題/タスクリストに限定）をリストアップし、オープンなブロッカー（`issue_dependencies_summary.blocked_by > 0`、または`Blocked by`ラインのオープン課題）や担当者がいるものは除外。マップ順で最初のものが勝者。
- **クレーム**: `gh issue edit <n> --add-assignee @me`、セッション最初の書き込み。
- **解決**: `gh issue comment <n> --body "<answer>"`、次に`gh issue close <n>`、その後マップのこれまでの決定へのコンテキストポインタ（要点+リンク）を追加。
