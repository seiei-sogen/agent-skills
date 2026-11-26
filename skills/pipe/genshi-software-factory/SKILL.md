---
name: genshi-software-factory
description: Genshi Software Factory。開いている GitHub issue を2つの作業役に分けて、並べて直す。作業役は issue を1件ずつ、調査、計画、セルフレビュー、実装、コードレビュー、PR、CI が通ったらマージ、と回して次の issue へ進む。引数がなければ、リポジトリの「次にやること」の一覧か、開いている issue のすべてを扱う。issue をこのファクトリーで片付けるよう頼まれたときに使う。
---

# Genshi Software Factory

issue を作業役に分けて、並べて直す。作業役は2つまでである。
作業役は、渡された issue を1件ずつ直してマージし、次の issue へ進む。1つの issue に1つの PR を立てる。

このスキルを呼ばれたセッションは、調整役である。調整役は、issue を分け、作業役を起こし、終わりに記録を書く。issue は直さない。
作業役の手順は、[`worker-takes-each-assigned-issue-from-investigation-to-merge.md`](worker-takes-each-assigned-issue-from-investigation-to-merge.md) にある。

どのリポジトリでも使える。リポジトリごとに違うものは、次のように書く。

- `<owner>/<repo>`: `git remote get-url origin` で分かる。
- `<既定ブランチ>`: `gh api repos/<owner>/<repo> --jq .default_branch` で分かる。
- リポジトリの約束: `AGENTS.md`、`CLAUDE.md`、`README.md` に書いてあること。コミットメッセージ、PR の題と本文、作業記録は、約束にある言語で書く。約束になければ、日本語で書く。

扱う issue は、引数に番号があればその issue だけである。
引数がなければ、リポジトリの「次にやること」の一覧から取る。この一覧は、`README.md` か、リポジトリの約束が指す文書にある、これから進める issue を順に並べた節である。手順1でこの一覧を上から読み、番号が挙がっていて、まだ開いている issue を、書かれた順に扱う。「#73 から #83」のような範囲は、その間の番号をすべて含む。issue の番号がない項目（所有者が確かめる項目など）は、扱わずに飛ばす。
「次にやること」の一覧がないリポジトリでは、開いている issue のすべてを、番号の小さい順に扱う。
扱う issue が1件もなければ、何もせずに「終わるとき」へ進み、そう報告する。
途中で立てた issue は、この実行では扱わない。次の実行が拾う。

## 置き場

```
docs/issues/<日付>/                          1回の実行。日付は TZ=Asia/Tokyo date +%Y%m%d
├── issue-assignment-to-workers.json       扱う issue と、作業役への分け方。調整役だけが書く
└── issue-<番号>/                          その issue の作業役が書く
    ├── preliminary-investigation.json     その issue の事前調査
    └── fix-plan.adoc                      修正の計画と、そのセルフレビュー
```

どのファイルも、書き換える PR は1つだけにする。事前調査を issue ごとのファイルにするのも、そのためである。1つのファイルを複数の PR が書き換えると、後からマージする側が衝突する。

その日のディレクトリが既にあれば、それを使う。
途中から再開するときは、日付が変わっていても、いちばん新しい日付のディレクトリを使い、手順1からやり直す。PR が開いたままの issue は、渡された作業役が、その続きから進める。

## 1. issue を作業役に分ける

最新の `origin/<既定ブランチ>` から、記録のためのブランチを作る。名前は、セッションに指定されたブランチがあればそれ、なければ `genshi-software-factory-record-<日付>` にする。

```bash
git fetch --prune origin
git checkout -B <ブランチ> origin/<既定ブランチ>
```

開いている issue を取る。

```bash
gh api 'repos/<owner>/<repo>/issues?state=open&per_page=100&page=1' \
  --jq '.[] | select(.pull_request | not) | [.number, .title] | @tsv'
```

1ページが100件で埋まっていたら、`page` を増やして次のページも取る。

引数がなく、「次にやること」の一覧があるときは、そこに挙がった番号のうち、上のコマンドで開いていると分かったものだけを扱う。

扱う issue を、`issue-assignment-to-workers.json` に次の形で書く。issue の中身の調べは、作業役が手順2で、issue ごとの事前調査に書く。ここでは、分けるのに要るだけ調べる。

```json
{
  "base_commit": "調査したときの origin/<既定ブランチ> の SHA",
  "issues": [
    {
      "number": 171,
      "title": "issue の題",
      "summary": "issue が求めていること",
      "depends_on": [],
      "related_code": ["src/…"],
      "status": "queued",
      "assigned_to_worker": 1,
      "reason": "この status と、この作業役にした理由"
    }
  ]
}
```

- `status` は `queued`、`skipped`、`done` のどれかである。`done` は PR をマージしたことを表す。
- 所有者の判断が要る issue と、1つの PR に収まらない issue は `skipped` にする。`skipped` の issue に依存する issue も `skipped` にする。
- `related_code` は、その issue が触りそうなファイルの見込みである。issue の本文と、コードの検索から出す。
- `assigned_to_worker` は 1 か 2 で、`queued` の issue にだけ書く。
  - 依存でつながる issue は、同じ作業役に渡す。`related_code` が重なる issue も、同じ作業役に渡す。2つの作業役が同じファイルを書くと、後からマージする側が衝突するからである。
  - 残りは、2つの作業役の件数がそろうように分ける。
  - `issues` には、作業役が片付ける順に並べる。「次にやること」の一覧から取ったときは、その順にする。ただし、依存される issue が後ろにあれば、それを先にする。それ以外のときは、依存される issue を先に、小さい issue を先にする。
  - `queued` の issue がすべて1つの作業役に集まるなら、作業役は1つにする。

`queued` の issue が1件もなければ、何も push せずに、「終わるとき」へ進む。

`issue-assignment-to-workers.json` をコミットして push する。クラウド環境のコンテナは、作業役を待つあいだに回収されることがあるからである。

```bash
git push --force-with-lease -u origin <ブランチ>
```

この手順は、`issue-assignment-to-workers.json` の扱う issue のすべてに `status` と `reason` があり、`queued` の issue のすべてに `assigned_to_worker` があれば終わりである。

## 2. 作業役を起こして、報告を待つ

作業役ごとに、次の依頼を渡す。`<このスキルのディレクトリ>` は、この `SKILL.md` があるディレクトリの絶対パスである。最後の1行は、クラウド環境でだけ書く。

```
<このスキルのディレクトリ>/worker-takes-each-assigned-issue-from-investigation-to-merge.md を読み、その手順で、issue #<番号>、#<番号> を、この順に片付ける。
リポジトリは <owner>/<repo>、既定ブランチは <既定ブランチ> である。
作業記録のディレクトリは docs/issues/<日付>/ である。
作業ブランチは genshi-software-factory-worker-<1 か 2> である。
終わったとき、または止まったときの報告は、send_message でセッション <調整役のセッション ID> へ送る。
```

| | クラウド環境 | 手元 |
|---|---|---|
| 起こし方 | `create_session`。`source_url` にこのリポジトリ、`outcome_branch` に依頼と同じ作業ブランチ | Agent ツール。`isolation: "worktree"` |
| 報告の届き方 | 作業役の `send_message` が、新しいターンとして届く。調整役のセッション ID は `get_session` で分かる | Agent ツールの結果 |

クラウド環境の作業役は、新しいコンテナで動く。環境のセットアップスクリプトが、このスキルを同じ場所に入れることを前提にしている。

2つの作業役は、1つの返事の中で続けて起こす。起こしたら、報告を待つ。クラウド環境では、ターンを終える。

この手順は、起こした作業役のすべてから報告が届けば終わりである。

## 3. 記録を書く

記録のためのブランチに、いまの既定ブランチを取り込む。

```bash
git fetch origin <既定ブランチ>
git merge --no-edit origin/<既定ブランチ>
```

次を書き直す。

- `issue-assignment-to-workers.json`。マージされた issue の `status` を `done` にする。片付かなかった issue と、作業役が飛ばした issue は、`status` を直し、`reason` に作業役の報告を書く。
- 作業役が、PR に入れられなかった事前調査を報告に書いてきたら、それを `issue-<番号>/preliminary-investigation.json` に書く。
- 「次にやること」の一覧。あるときだけ、いまの書き方に合わせて、次のように直す。
  - 直した issue を消す。`issue-assignment-to-workers.json` に残る issue、`skipped` のうち判断が要る issue、作業役が立てた issue を、進める順に書く。
  - 同じ文書に、終わったことの一覧や、いつの時点の状態かを示す日付があれば、それも直す。終わったことの一覧には、この実行の項目を1つ置き、`docs/issues/<日付>/` にリンクする。直した issue は、その項目に書き足す。

コミットして `git push` し、PR を立て、CI が通ったらマージする。PR の立て方、CI の待ち方、マージのしかたは、作業役の手順6と7と同じである。この PR は issue を閉じないので、本文に `Closes` は書かない。

## 終わるとき

最後に、作業役の報告を合わせて、次を報告する。

- マージした PR と、閉じた issue。
- `skipped` にした issue と、作業役が飛ばした issue と、その理由。
- 新しく立てた issue。
- 止まった作業役があれば、止まった手順と、その理由。
