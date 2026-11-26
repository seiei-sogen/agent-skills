# 作業役は、渡された issue を1件ずつ、調査からマージまで進める

Genshi Software Factory（[`SKILL.md`](SKILL.md)）の調整役から、issue の番号の並びと、リポジトリ `<owner>/<repo>` と、`<既定ブランチ>` と、作業記録のディレクトリ `docs/issues/<日付>/` を渡されて始める。
渡された順に、issue を1件ずつ直してマージし、次の issue へ進む。1つの issue に1つの PR を立てる。

同じときに、もう1つの作業役が、別の issue を別のブランチで直している。既定ブランチは、作業の途中で進む。
書くのは、渡された issue の `docs/issues/<日付>/issue-<番号>/` だけである。
リポジトリの「次にやること」の一覧と、`docs/issues/<日付>/issue-assignment-to-workers.json` は書かない。調整役が、実行の終わりに書く。

リポジトリの約束とは、`AGENTS.md`、`CLAUDE.md`、`README.md` に書いてあることである。コミットメッセージ、PR の題と本文、作業記録は、約束が決めた言語で書く。決めていなければ、リポジトリの文書と同じ言語で書く。

計画と実行は、pstack の poteto-mode で行う。始める前に、Skill ツールで `pstack:poteto-mode` を呼ぶ。
手順2から5は、issue に合う poteto-mode の playbook（Bug fix、Feature、Refactoring など）に従って進め、その計画を `fix-plan.adoc` に書く。
PR の題と本文、CI の待ち方、マージは、poteto-mode の Opening a PR、Babysit、Shipping や pstack の `worker.md` ではなく、このファイルの手順6と7に従う。

## 1つの issue の流れ

### 1. 作業ブランチを用意する

最新の `origin/<既定ブランチ>` から作る。名前は、調整役に渡された名前にする。
前の issue と同じ名前を使い回すこともあるので、作り直す形にする。
`--prune` を付けて全体を取るのは、手順6の `--force-with-lease` がリモートのブランチのいまの位置を知っている必要があるからである。

```bash
git fetch --prune origin
git checkout -B <ブランチ> origin/<既定ブランチ>
```

その issue の PR が開いたまま残っていれば、ブランチを作り直さない。計画、ブランチ、PR のどこまで済んだかを見て、済んでいない最初の手順から続ける。

### 2. 事前調査を書いて、計画を立てる

issue の本文とコメントを読み、関係するコードとテストを調べる。結果を `docs/issues/<日付>/issue-<番号>/preliminary-investigation.json` に、次の形で書く。

```json
{
  "number": 171,
  "title": "issue の題",
  "base_commit": "調べたときの origin/<既定ブランチ> の SHA",
  "summary": "issue が求めていること",
  "depends_on": [],
  "status": "next",
  "reason": "この status にした理由",
  "current_behavior": "いまの振る舞いと、それを確かめたコマンドと出力",
  "how_it_works_now": "入口から、問題の起きる場所までの、コードの流れ。読んだファイルと関数を挙げる",
  "why_it_is_this_way": [
    {
      "claim": "いまの形になった理由",
      "source": "コミットの SHA、PR や issue の番号、文書のパス",
      "kind": "quoted か inferred"
    }
  ],
  "unanswered_by_the_record": ["記録を探しても分からなかったこと"],
  "related_code": ["src/…: 関数名"],
  "related_tests": ["test/…"],
  "affected_ci_checks": ["影響を受ける CI の検査の名前"],
  "risks": []
}
```

- `status` は `next`、`skipped`、`done` のどれかである。`done` は PR を立てたことを表す。
- 不具合の issue は、いまのコードで再現してから `current_behavior` に書く。
- `how_it_works_now` は、pstack の `how` スキルに従って調べる。この issue に関係する範囲に絞る。
- `why_it_is_this_way` は、pstack の `why` スキルに従って調べる。コードからではなく、記録から答える。関係するコードを入れたコミットと、その PR、issue、リポジトリの文書を、`git log -S`、`git blame`、`gh api` で辿る。書いた人の言葉は `quoted`、自分の推測は `inferred` にする。
- `how` と `why` は Skill ツールでは呼べない。poteto-mode の `SKILL.md` と同じ階層の `../how/SKILL.md` と `../why/SKILL.md` を読んで、それに従う。

事前調査は、各項目が、読んだコードか、実行したコマンドか、引用元のある記録に基づいていれば終わりである。

調べた結果、所有者の判断が要る issue と、1つの PR に収まらない issue は、直さずに飛ばす。直そうとしている振る舞いが、わざと選ばれたものだと `why_it_is_this_way` で分かったら、所有者の判断が要る。渡された issue のうち、それに依存する issue も飛ばす。
飛ばす issue の事前調査は、`status` を `skipped` にして、次の issue の PR に入れる。次の PR がなければ、その中身を、終わるときの報告に書く。調整役が、記録の PR に入れる。

計画は `docs/issues/<日付>/issue-<番号>/fix-plan.adoc` に AsciiDoc で書く。その issue の事前調査をもとにする。節は次の通りである。

- `== 目的`: issue が求めていることと、終わりの条件。
- `== 現状`: いまの振る舞いと、それを確かめたコマンドと出力。関係するコードとテスト。リスク。
- `== 変更`: 変えるファイルと関数、新しく作るファイル。命名や、ファイルの分け方は、リポジトリの約束に従う。
- `== テスト`: 最初に書く、失敗するテスト。
- `== 確認`: CI の検査への影響。作り直す生成物（スナップショット、記録した期待値など）があれば、それも挙げる。
- `== 範囲外`: この PR でしないこと。

### 3. 計画をセルフレビューする

issue の本文とコメントに照らして、計画を3回見直す。毎回、次の3つをすべて見る。

- issue が求めることの一つ一つに、変更とテストが対応しているか。
- 変更が届くべき呼び出し元、テスト、記録がすべて挙がっているか。
- リポジトリの約束に沿っているか。

1回ごとに計画を直し、見つけたことと直したことを、末尾の `== セルフレビュー` の `=== 1回目`、`=== 2回目`、`=== 3回目` に書く。
2回目と3回目は、前の回で直した箇所も含めて、計画を頭から読み直す。何も見つからなかった回も、そう書く。途中の回で何も見つからなくても、3回やる。

### 4. 実装する

計画に従い、`/superpowers:test-driven-development` で実装する。計画と違うことをしたら、計画にそう書き足す。

この手順は、CI が行う検査を、手元ですべて通せば終わりである。
検査のコマンドは、リポジトリの約束と、CI の設定（`.github/workflows/` など）から見つける。手元で行えない検査は CI に任せ、手順6の PR の本文にそう書く。デプロイやリリースの手順は、検査ではないので実行しない。

### 5. コードレビューで直す

`git fetch origin <既定ブランチ>` のあと、Claude Code の `/code-review` を実行する。Skill ツールなら、スキル `code-review` に次の引数を渡す。
最後の3語を落とすと、コミットしていない差分がレビューから漏れる。

```
high --fix origin/<既定ブランチ>...HEAD plus uncommitted changes
```

直したら、手順4の検査をもう一度すべて通す。

この issue の範囲外の指摘で、直す価値があるものは、新しい issue にする。

```bash
gh api repos/<owner>/<repo>/issues -f title='…' -F body=@<本文のファイル>
```

### 6. PR を立てる

この issue の事前調査の `status` を `done` にする。
残りをコミットし、下の「既定ブランチを取り込む」を行ってから push して、PR を立てる。
リモートに前の issue のマージ済みのブランチが残っていることがあるので、`--force-with-lease` で上書きする。手順1のあとに誰かが push していれば、push は断られる。そのときは止める。

```bash
git push --force-with-lease -u origin <ブランチ>
gh api repos/<owner>/<repo>/pulls -f base=<既定ブランチ> -f head=<ブランチ> \
  -f title='…' -F body=@<本文のファイル>
```

本文には次を書く。

- `Closes #<番号>`
- 何を、どう直したか。
- 計画のパス。
- 手順4の検査の結果と、手元で行えなかった検査。
- コードレビューで直したことと、立てた issue。

### 7. CI が通ったらマージする

push するたびに、まず、PR が既定ブランチと衝突していないかを見る。

```bash
gh api repos/<owner>/<repo>/pulls/<PR 番号> --jq '.mergeable | tostring'
```

- `null` なら、GitHub が計算している途中である。数秒おいて取り直す。
- `false` なら、「既定ブランチを取り込む」を行って push し、見直す。衝突している PR では CI が走らないので、待っても終わらない。
- `true` なら、CI を待つ。

クラウド環境では `subscribe_pr_activity` で PR を購読してターンを終え、CI の通知で再開する。手元では `gh pr checks <PR 番号> --watch` で待つ。

CI が落ちたら、原因を直して push し、PR の本文をいまの内容に合わせて更新する（`gh api -X PATCH repos/<owner>/<repo>/pulls/<PR 番号> -F body=@<本文のファイル>`）。そしてまた待つ。
もう1つの作業役のマージと合わさって初めて壊れたものも、この PR で直す。PR の CI は、push したときの既定ブランチと合わせた結果を検査している。

push した最後のコミットに、check run か commit status が1件以上あり、次の2つがそろったら、もう一度 `mergeable` を見る。`true` なら、squash でマージする。

- check run のすべてが `completed` で、`conclusion` が `success`、`skipped`、`neutral` のどれかである。
- commit status が0件であるか、その `state` が `success` である。

CI のないリポジトリでは、待たない。CI の設定がなく、既定ブランチの最新のコミットにも check run と commit status が1件もなければ、CI はない。手順4の検査が通っていて、`mergeable` が `true` なら、マージする。
リポジトリが squash を許していなければ、許している方法でマージする。それでもマージが断られたら（レビューが必須になっているなど）、そこで止める。
待つあいだに既定ブランチが進んでいても、衝突していなければ、取り込み直さずにマージする。
手元では、作業ブランチをリモートから消す。クラウド環境ではブランチを消せないので残し、購読をやめる。残したブランチは、次の issue の手順6で上書きされる。

```bash
gh api repos/<owner>/<repo>/commits/<SHA>/check-runs \
  --jq '.check_runs[] | [.name, .status, .conclusion] | @tsv'
gh api repos/<owner>/<repo>/commits/<SHA>/status --jq '[.state, .total_count] | @tsv'
gh api -X PUT repos/<owner>/<repo>/pulls/<PR 番号>/merge -f merge_method=squash -f sha=<SHA>
gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/<ブランチ>  # 手元だけ
```

次の issue の手順1へ進む。

## 既定ブランチを取り込む

もう1つの作業役が先にマージした変更を、自分のブランチへ入れる。

```bash
git fetch origin <既定ブランチ>
git merge --no-edit origin/<既定ブランチ>
```

何も取り込まれなければ、ここで終わりである。取り込まれたら、次のようにする。

- コマンドが生成するファイル（スナップショット、ロックファイル、記録した期待値など）の衝突は、手で混ぜない。どちらかの側を取り、それを生成するコマンドで作り直す。作り直した結果は、両方の側の変更を合わせたものになる。どちらの側の変更からも説明できない差が出たら、コミットせずに、原因を直す。
- ほかの衝突は、両方の変更が生きるように解く。既定ブランチの側が何をしたかは、そのコミットの PR の本文と、`docs/issues/` の計画で分かる。
- 手順4の検査をもう一度すべて通して、コミットする。
- 解いても検査が通らなければ、`origin/<既定ブランチ>` からブランチを作り直し、計画に従って実装し直す。作り直したあとの push は、`--force-with-lease` にする。

## 終わるとき

渡された issue がなくなったら終わる。原因の分からないまま CI が落ち続けるときと、マージが断られたときも、そこで止める。
最後に、次を調整役へ報告する。クラウド環境では、`send_message` で、依頼にあったセッションへ送る。

- マージした PR と、閉じた issue。
- 飛ばした issue と、その理由。PR に入れられなかった事前調査があれば、その中身。
- 新しく立てた issue。
- 止めたなら、止めた手順と、その理由。
