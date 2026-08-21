# GitHub issue から要件定義書を初期化する

このファイルは `pipe-requirements-to-pr` の入力が GitHub issue URL の場合だけ読む。
ここで生成した要件定義書を親スキルの共通入力に設定し、Phase 1 以降は既存の流れを実行する。

## issue と対象リポジトリを確定する

入力 URL が `https://github.com/<owner>/<repo>/issues/<number>` 形式の単一 issue を指すことを確認する。
クエリやフラグメントがある場合は、それらを除いた URL を正規化した入力として扱う。

現在の Git リポジトリの remote と issue URL の `<owner>/<repo>` を照合する。
実装対象のリポジトリだと確認できない場合は worktree を作らず、相違を報告して対象リポジトリを確認する。

次の情報を GitHub から取得する。

- issue 番号
- タイトル
- 本文
- ラベル
- コメント
- state
- 正規化した URL

GitHub CLI を利用できる場合は、URL をそのまま指定して取得する。

```bash
gh issue view '<issue-url>' --json number,title,body,labels,comments,state,url
```

issue を取得できない、または issue が存在しない場合は、ブランチや worktree を作らず停止する。

## ブランチ名を決める

`suggest-git-branch-name` を使い、issue 番号、タイトル、本文、ラベル、および要件として採用できるコメントを入力して第一候補を1件得る。
コメントは決定事項または再現条件を補う場合に使い、本文と矛盾する内容を推測で採用しない。

候補を `git check-ref-format --branch` で検証する。
候補の最初の `/` より後ろを `<branch-tail>` とする。
たとえば `feat/issue211-backend-fix-validation-issues-count-mismatch` の `<branch-tail>` は `issue211-backend-fix-validation-issues-count-mismatch` である。

`<branch-tail>` が空、絶対パス、複数階層、または `..` を含む場合は後続処理を始めず、ブランチ名を作り直す。

## `git wt` で worktree を用意する

ブランチ作成前に `git worktree list --porcelain`、ローカルブランチ、対象候補パスを確認する。

- 対象ブランチの worktree が存在しなければ、リポジトリルートで `git wt '<branch-name>'` を実行する。
- 対象ブランチの worktree が既に1件だけ存在する場合は、同じ issue の作業であり既存変更を保持できることを確認して再利用する。
- 同じブランチに複数の候補、別用途のディレクトリ、または安全に保持できない変更がある場合は停止して衝突を報告する。

`git wt` の代わりに別の worktree 作成コマンドへ置き換えない。
`git wt` が利用できない、または失敗した場合は、別コマンドで作成を続けずに実行結果と再開点を報告して停止する。
実行後に `git worktree list --porcelain` を再取得し、`branch refs/heads/<branch-name>` に対応する worktree パスを1件だけ特定する。
その worktree で `git branch --show-current` が生成したブランチ名と一致することを確認する。

以後のファイル操作と Git コマンドは、特定した worktree を作業ルートとして実行する。
元の worktree へ要件定義書や実装変更を作成しない。

## 要件定義書を作成する

worktree ルートからの相対パスとして、次を作成する。

```text
docs/task-requirements/<branch-tail>/
docs/task-requirements/<branch-tail>/req-<branch-tail>.adoc
```

先頭の `docs` は worktree 内のリポジトリ相対パスであり、ファイルシステムルートの `/docs` ではない。
既存ディレクトリや同名ファイルがある場合は、issue URL と内容が今回の対象に一致することを確認する。
別 issue の成果物なら上書きせず停止する。

[成果物の契約](artifact-contracts.md) に従い、取得した issue の内容から有効な AsciiDoc 要件定義書を作成する。
少なくとも次を追跡できるようにする。

- 出典となる issue 番号、タイトル、URL
- 背景と解決したい問題
- 現在の挙動と期待する挙動
- 対象範囲と対象外
- 機能要件と、issue から読み取れる制約
- 検証可能な受け入れ条件
- 例外、失敗時、境界条件
- issue だけでは確定できない未決事項

issue に根拠がない仕様は確定事項として補わない。
曖昧な点は未決事項として明示し、親スキルの壁打ちと品質ゲートで解消する。

## 共通パイプラインへ合流する

生成した `req-<branch-tail>.adoc` を親スキルの入力ファイルに設定する。
issue 番号は `<issue-token>` を決める確認済み情報として引き継ぐ。

次のすべてを確認できたら初期化を完了し、親スキルの「入力と成果物を確定する」へ戻って Phase 1 以降を続ける。

- worktree が生成したブランチに登録されている
- 作業ルートがその worktree を指している
- 要件ディレクトリ名が `<branch-tail>` と完全に一致する
- 要件定義書名が `req-<branch-tail>.adoc` と完全に一致する
- 要件定義書が有効な AsciiDoc で、出典 issue を一意に追跡できる
