# 課題トラッカー: GitLab

このリポジトリの問題と仕様は GitLab のイシューとして管理されています。すべての操作には [`glab`](https://gitlab.com/gitlab-org/cli) CLI を使用してください。

## 慣習

- **課題を作成する**: `glab issue create --title "..." --description "..."`。複数行の説明にはヒアドキュメントを使用してください。`--description -`を渡してエディタを開きます。
- **問題を読む**: `glab issue view <number> --comments`。機械可読の出力には`-F json`を使用してください。
- **問題をリスト**: 適切な `--label` フィルターを使用した `glab issue list -F json`。
- **問題にコメントする**: `glab issue note <number> --message "..."`。GitLabではコメントを「ノート」と呼びます。
- **ラベルを適用/削除する**: `glab issue update <number> --label "..."` / `--unlabel "..."`。複数のラベルはカンマで区切るか、フラグを繰り返して指定できます。
- **クローズ**: `glab issue close <number>`。`glab issue close`はクローズ時にコメントを受け付けないため、まず`glab issue note <number> --message "..."`で説明を投稿してからクローズしてください。
- **マージリクエスト**: GitLabではPRのことを「マージリクエスト」と呼びます。`glab mr create`、`glab mr view`、`glab mr note`などを使用し、`gh pr ...`と同じ形で`pr`の代わりに`mr`、`comment`/`--body`の代わりに`note`/`--message`を使用します。

`git remote -v`からリポジトリを推測します；`glab`はクローン内で実行されると自動的にこれを行います。

## マージリクエストはトリアージの表面として使用されます

**リクエストのサーフェスとしてのMR：いいえ。** _(このリポジトリが外部マージリクエストを機能リクエストとして扱う場合は`yes`に設定してください；`/triage-matt-ryu`がこのフラグを読み取ります。)_

`yes`に設定すると、MRは課題と同じラベルおよび状態を通過し、`glab mr`相当を使用します：

- **MRを読む**：`glab mr view <number> --comments`および`glab mr diff <number>`（差分用）。
- **トリアージ用に外部MRをリストアップ**: `glab mr list -F json`、その後、作成者がプロジェクトメンバー/オーナーでないMRのみを残します（メンテナの進行中作業ではなく、コントリビュータのMR）。
- **コメント / ラベル付け / クローズ**: `glab mr note`, `glab mr update --label`/`--unlabel`, `glab mr close`。

GitHubとは異なり、GitLabでは課題とMRが別々に番号付けされているため、メンテナが指す対象を知っていれば`#42`は明確です。

## スキルが「課題トラッカーに公開」と言うとき

GitLabの課題を作成します。

## スキルが「関連するチケットを取得」と言うとき

`glab issue view <number> --comments`を実行します。

## ウェイファインディング操作

`/wayfinder-matt-ryu`で使用されます。**マップ**は単一の課題で、**子**課題がチケットとして存在します。

- **マップ**: `wayfinder:map`というラベルが付いた単一の課題で、Notes / Decisions-so-far / Fogの内容を保持します。`glab issue create --label wayfinder:map`。（GitLabのネイティブエピック対応の階層では、エピックがマップを保持する場合があります。ラベル付きの課題はどこでも機能します。）
- **子供用チケット**：説明の上部に`Part of #<map>`を記載し、ラベル`wayfinder:<type>`（`research`/`prototype`/`grilling`/`task`）をつけたもの。請求されると、そのチケットは担当開発者に割り当てられます。
- **ブロッキング**: GitLabの**ネイティブブロッキングリンク**、標準的でUIに表示される表現。`/blocked_by #<n>`クイックアクションで追加し、ノートとして投稿します（`glab issue note <child> --message "/blocked_by #<blocker>"`）。ネイティブブロッキングリンクはPremium/Ultimate機能です；無料プラン（または利用できない場合）では、説明の先頭に`Blocked by: #<n>, #<n>`行を代わりに追加してください。チケットは、すべてのブロッカーがクローズされたときにブロック解除されます。
- **フロンティアクエリ**: `glab issue list -F json` をマップの子に限定し、次のいずれかがある場合は削除する: 開いているブロッカーがある場合（ネイティブ `blocked_by` リンクで開いている問題 (`glab api projects/:id/issues/:iid/links`)）、または `Blocked by` 行の開いている問題、または担当者; マップの順序で最初のものが優先される。
- **クレーム**: `glab issue update <n> --assignee @me`、セッションの最初の書き込み。
- **解決**: `glab issue note <n> --message "<answer>"`、次に `glab issue close <n>`、そしてコンテキストポインタ（gist + リンク）をマップの Decisions-so-far に追加する。
