# コード考古学（git + リポジトリ内）

## このソースに含まれるもの

- コミット履歴（メッセージ、日付、作者、差分）
- PR の説明、レビューコメント、議論のスレッド（`gh` 経由）
- インラインのコードコメント、TODO、FIXME、非推奨の注記
- リポジトリが保持していれば、ADR（アーキテクチャ決定記録）
- テスト。名前とアサーションには、変更の動機となったエッジケースが込められていることが多い
- 同じコミットで変更された関連ファイル（共変更のシグナル）
- CHANGELOG のエントリ、リポジトリ内のリリースノート
- コミットメッセージや PR 本文で言及された issue やチケットの ID

最も信頼できるソースであり、コードに直接結び付いていて、最も網羅的でもある。リポジトリを経由したものはすべてここにあるはずだ。

## 検索の仕方

シードとなるコミット一覧を広げる。

```bash
# Full history of the file through renames
git log --follow --oneline -- <file>

# Pickaxe: commits that added or removed this exact text
git log -S '<exact_string_from_code>' -- <file>

# Or for patterns:
git log -G '<regex>' -- <file>

# Who wrote each line and when
git blame -L <start>,<end> <file>

# The full diff of a specific commit
git show <hash>

# Commits between two points affecting this file
git log <old>..<new> -p -- <file>
```

実質的な内容を持つコミットごとに、PR のコンテキストを取得する。

```bash
# Find the PR number from the merge commit or branch
git log -1 --format=%B <hash>

# Full PR context: body, review comments, linked issues
gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews,files

# The --json reviews and comments fields are where the real signal is
```

コード外のドキュメントを探す。

```bash
# ADRs often live in docs/adr/ or similar
rg -l -i 'architecture.decision' --glob '*.md'

# TODOs and FIXMEs near the target
rg -n -C2 '(TODO|FIXME|HACK|XXX|NOTE)' <target_file>

# Related tests. Names often encode the "why"
rg -l '<symbol>' --glob '*test*'
```

## ここでの良い証拠とはどのようなものか

- 変更内容だけでなく、解決しようとしている問題を説明した PR の説明（「これは X を引き起こしていたページネーションのバグを修正する」）
- 代替案が議論された長いレビュースレッド
- 対象行の近くにあり、自明でない制約を説明しているインラインコメント
- `test_handles_edge_case_when_X` のような名前で、コードの動機となったエッジケースを明かしているテスト
- チケットやインシデントの ID を参照しているコミットメッセージ
- ユーザーに見える根拠説明を要約した CHANGELOG のエントリ

## よくある落とし穴

- **スカッシュマージによる履歴の平坦化。** リポジトリが PR をスカッシュしている場合、ブランチ履歴の個々のコミットは失われている。代わりに PR 本文とコメントを頼る。
- **誤解を招くコミットメッセージ。** 「小さなリファクタ」が意図的な振る舞いの変更を隠していることがある。メッセージではなく差分を見る。
- **カーゴカルト化したパターン。** 作者は理由を理解せずにパターンをコピーしたかもしれない。そのパターンがコードベースのもっと前の時点で生まれたものか確認し、*その*コミットを調査する。
- **ボットのコミットと自動マージ。** Dependabot、Renovate、自動バックポートは通常、動機を伴わない。意図を探すときはスキップする。
- **コードを意図の証拠として扱うこと。** コードそれ自体は、それが存在する理由の証拠ではない。証拠はコミットメッセージ、PR、コメント、テスト、ドキュメントから得る。「関数の名前が X である」を意図の証拠として引用しない。

## 返すもの

問いに関係するすべてのコミット、PR、コメントを、次の情報とともに返す。
- 正確なテキスト（引用）
- ハッシュ / PR 番号 / file:line
- 作者と日付
- 直接的（問いに明示的に答えている）か状況的か
