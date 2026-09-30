# ノートを作成する

ノート作成では、ユーザーはブラウザまたは CLI からタイトル付きのノートを保存し、未完成の下書きをキャンセルし、保存したノートを 2 つ目のユーザー向け表示から確認できる。

## Sub-features

- `create-open` は、ブラウザの各入口から空のエディタを開く。
- `create-save` は、タイトルと本文を永続化する。
- `create-cancel` は、未完成のブラウザ下書きを破棄する。
- `create-cli` は、ターミナルから同じ形のノートを作成する。

## How to get to it (user POV)

- ブラウザのツールバーで `New note` ボタンを選ぶ。
- フォーカスが編集可能なフィールドの外にある状態で、ブラウザで `n` を押す。
- ターミナルで `notes create --title <title> --body <body>` を実行する。

## Driving it with control-notes

Preconditions:

- Notes が `http://127.0.0.1:4173` で正常に動作している。
- `Release checklist` というタイトルのノートが存在しない。
- `control-notes doctor` が期待する URL と使い捨てのデータディレクトリを報告する。

- **エディタを開く。** `New note` を選ぶ。`control-notes browser click --role button --name "New note"` を実行する。`Note editor` という名前のフォームが現れ、`Title` テキストボックスにフォーカスがある。
- **内容を入力する。** タイトルと本文を入力する。`control-notes browser fill --role textbox --name "Title" --value "Release checklist"` と `control-notes browser fill --role textbox --name "Body" --value "Tag and publish"` を実行する。`Save note` ボタンが有効になる。
- **ノートを保存する。** `Save note` を選ぶ。`control-notes browser click --role button --name "Save note"` を実行する。`Note saved` という名前のステータスが現れ、見出しが `Release checklist` になる。
- **永続化を確認する。** ノート一覧に戻り、ノートを再度開く。`control-notes browser click --role link --name "All notes"` と `control-notes browser click --role link --name "Release checklist"` を実行する。エディタに保存した両方の値が表示される。
- **下書きをキャンセルする。** 新しいノートを開き、`Discard me` を入力し、`Cancel` を選ぶ。`control-notes browser click --role button --name "New note"`、`control-notes browser fill --role textbox --name "Title" --value "Discard me"`、`control-notes browser click --role button --name "Cancel"` を実行する。ノート一覧に戻り、`Discard me` のリンクは存在しない。
- **CLI の入口。** 2 つ目のノートを作成する。`control-notes cli -- notes create --title "CLI note" --body "Created from terminal" --format json` を実行する。終了コードは `0` で、stdout に新しいノートの ID とタイトルが含まれる。
- **証明。** `All notes` から保存した両方のノートを再度開く。`control-notes browser snapshot --aria --path artifacts/create-note/list.aria.txt` と `control-notes browser screenshot --path artifacts/create-note/list.png` を実行する。成果物に `Release checklist` と `CLI note` が表示されている。

## Gotchas

- テキストボックスにフォーカスがある状態で `n` を押すと、新しいエディタを開くのではなくその文字が入力される。
- タイトルは保存時にトリムされる。下書きの入力値ではなく、描画されたタイトルをアサートする。
- 保存ステータスだけでは証明として不十分である。一覧からノートを再度開く。
- フィクスチャのクリーンアップ中に `Release checklist` と `CLI note` を削除するが、それらの証明の成果物は保持する。
