---
name: decision-inbox
description: claude.ai の Artifact「判断インボックス」に、ユーザーの判断が要る質問を図付きで出し、ユーザーが選んだ答えを読んで作業を続ける。「インボックスで聞いて」と頼まれたとき、ユーザーが「インボックスで答えた」と言ったとき、作業の進み具合をインボックスに載せるときに使う。
---

# 判断インボックス

ユーザーは文字をほとんど読まず、図を見て選ぶだけで判断する。
質問は、図を見れば選べる形でインボックスに出す。

読み書きはすべて ArtifactData で行い、`url` にインボックスの URL を渡す。

## 手順

### 1. インボックスを読む

Artifact ツールの `list`（`limit: 200`）で、タイトルが「判断インボックス」のアーティファクトを探し、その URL を使う。
見つからなければ、ユーザーに URL を聞く。

`settings/inbox` を get し、`tasks` を list する。
`away` の値と、`answer` を持つタスクの一覧が手元にそろったら完了。

### 2. 答えを取り込む

`answer` を持つタスクごとに、次をまとめて batch で書く。

- `decided` に、選んだ選択肢の `label` を足す。todo なら「<question.title> を済ませた」、memo があればその要点も足す
- `question` と `answer` を消す
- `state`、`phase`、`updatedAt` を、これから進める内容に合わせる

memo に質問が書かれていたら、作業に戻る前にターミナルで答える。
`answer` を持つタスクが残っていなければ完了。

### 3. 質問を出す

判断が要るたびに、そのタスクのドキュメントに `question` を書き、`state` を `"waiting"` にする。
タスクのドキュメントがなければ作る。

`away` が true のあいだは質問を出さない。
推奨案を選んだものとして、`decided` に「<label>（離席中に推奨案で決定）」を足し、作業を続ける。

書いたら、ターミナルに「インボックスに Q3 を出しました」と 1 行で伝える。
答えを待たずに進められる作業は進め、なければターンを終える。

### 4. 進み具合を載せる

作業の区切りごとに、そのタスクの `state`、`phase`、`updatedAt` を更新する。
止まったら `state` を `"blocked"` にして、理由を `note` に書く。
タスクが終わったら `state` を `"done"` にする。

## tasks/<task-id>

1 タスクを 1 ドキュメントにする。
`task-id` は英小文字とハイフンの短い slug にする。

- `title`: タスク名
- `state`: `"waiting"`（あなたの番）、`"running"`（動いている）、`"blocked"`（止まっている）、`"next"`（次にやること）、`"done"`（終わったこと）
- `phase`: いまの段階と全体の段数。例 `"置き場所 (2/3)"`
- `updatedAt`: ISO 8601。一覧の並び順と「3 分前」の表示に使う
- `note`: 一覧の右下に出す短い補足（任意）
- `decided`: 決まったことの文字列の配列
- `question`: `id`、`kind`（`"choice"` か `"todo"`）、`title`、`body`、`points`、`options`、`context`、`refs`
  - `id`: 表示用の番号。choice は `Q`、todo は `T` に、インボックス内でまだ使っていない数字を続ける
  - `options`: `[{ key: "A", label, sub, recommended, figure }]`
  - `context`: `[{ title, figure, text }]`。画面の右側に番号付きで並ぶ
- `answer`: `{ choice, memo, at }`。ページだけが書き、書くと同時に `state` を `"running"` にする。`choice` は選択肢の `key`、todo なら `"done"`、メモだけなら `null`
- `example`: true のタスクは最初に入れたサンプル。ユーザーに頼まれたら消す

`settings/inbox` は `away`（離席中なら true）を持つ。

## 質問の書き方

- `title` は 1 行の疑問文にする。例「保存ボタンはどこに置く？」
- `body` は 2 文までにし、何が問題で何を選ぶのかだけを書く
- `options` は 2〜4 個にし、`recommended: true` は 1 つだけに付ける
- `sub` には、その選択肢の利点と欠点を 1 行で書く
- 各選択肢に、選んだ後の姿を描いた `figure` を付ける。画面なら見本の画面、処理なら流れ図
- `context` には、なぜ判断が要るのかを示す図を 1〜2 個置き、数値には測り方を `text` に添える
- `refs` には、根拠にした実物（他のアプリ、既存のコード、ドキュメント）を書く
- ユーザーが手を動かす作業は `kind: "todo"` で出し、`body` に手順と、終わったら「終わった」を押すことを書く

## 図

`figure` は SVG の文字列で、ページが DOMPurify を通して表示する。
script、イベント属性、外部画像は消える。

- `viewBox` を付け、`width` と `height` は付けない。ページが枠の幅に合わせる
- 選択肢の図は `viewBox="0 0 240 150"`、context の図は横 300 を目安にする
- 色は次の CSS 変数で書くと、ライトとダークの両方で読める
  - `var(--fg)`、`var(--muted)`: 文字と線
  - `var(--panel)`、`var(--sunken)`、`var(--line)`: 画面の地、くぼみ、罫線
  - `var(--accent)` と、その上の文字 `var(--on-accent)`: 推奨やボタン
  - `var(--good)`、`var(--warn)`: よい結果、悪い結果
- 文字は `font-size` 10〜13 で、線や図形と重ならない位置に置く
- 属性値を一重引用符で囲むと、JSON に入れるときにエスケープが要らない
