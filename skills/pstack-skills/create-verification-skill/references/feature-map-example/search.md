# ノートを検索する

検索では、ユーザーはタイトルまたは本文のテキストでノートを見つけ、一致したノートを確認し、一致なしと検索が利用できない状態を区別できる。

## Sub-features

- `search-open` は、サポートされる各ブラウザ入口から検索を開く。
- `search-match` は、ノートのデータを変更せずにタイトルと本文の一致を返す。
- `search-open-result` は、結果をノートエディタで開く。
- `search-empty` は、一致のないクエリに対して完全な空状態を表示する。
- `search-clear` は、クエリを削除して最近のノートの表示を復元する。
- `search-cli` は、ターミナルから同じ一致ノートを返す。

## How to get to it (user POV)

- ブラウザのツールバーで `Search` ボタンを選ぶ。
- フォーカスが編集可能なフィールドの外にある状態で、ブラウザで `/` を押す。
- ターミナルで `notes search <query>` を実行する。

## Driving it with control-notes

Preconditions:

- Notes が `http://127.0.0.1:4173` で正常に動作している。
- 使い捨てのデータディレクトリに、本文テキストが `Draft budget` の `Quarterly plan` が含まれている。
- `control-notes doctor` が期待する URL とデータディレクトリを報告する。

- **ツールバーからの入口。** `Search` ボタンを選ぶ。`control-notes browser click --role button --name "Search"` を実行する。`Search notes` という名前のダイアログが現れ、その検索ボックスにフォーカスがある。
- **キーボードからの入口。** ダイアログを閉じ、ページにフォーカスし、`/` を押す。`control-notes browser press --key "/"` を実行する。同じダイアログが現れ、ページにスラッシュは挿入されない。
- **タイトルの一致。** `quarterly` を入力する。`control-notes browser fill --role searchbox --name "Search notes" --value "quarterly"` を実行する。`Search results` リストに `Quarterly plan` が含まれ、`Grocery list` は含まれない。
- **本文の一致。** クエリを `budget` に置き換える。`control-notes browser fill --role searchbox --name "Search notes" --value "budget"` を実行する。結果 `Quarterly plan` が本文一致の抜粋とともに表示されたままになる。
- **結果を開く。** `Quarterly plan` を選ぶ。`control-notes browser click --role link --name "Quarterly plan"` を実行する。ダイアログが閉じ、エディタの見出しが `Quarterly plan` になる。
- **空状態。** 検索を再度開き、`volcano` を入力する。`control-notes browser fill --role searchbox --name "Search notes" --value "volcano"` を実行する。検索完了後に `No matching notes` という名前のステータスが現れる。
- **クエリをクリアする。** `Clear search` を選ぶ。`control-notes browser click --role button --name "Clear search"` を実行する。検索ボックスが空になり、結果リストが `Recent notes` 領域に置き換わる。
- **CLI の一致。** ターミナルから検索する。`control-notes cli -- notes search "quarterly" --format json` を実行する。終了コードは `0` で、stdout にタイトルが `Quarterly plan` のオブジェクトが 1 つ含まれる。
- **CLI の不一致。** 存在しない値を検索する。`control-notes cli -- notes search "volcano" --format json` を実行する。終了コードは `0` で、stdout は `[]` である。
- **証明。** 結果が表示された状態を取得する。`control-notes browser snapshot --aria --path artifacts/search/results.aria.txt` と `control-notes browser screenshot --path artifacts/search/results.png` を実行する。両方の成果物から Notes、クエリ、`Quarterly plan` が識別できる。

## Gotchas

- エディタや検索ボックスにフォーカスがある状態で `/` を押すと、検索を開くのではなくテキストが挿入される。
- 結果は短いデバウンスの後に更新される。固定のスリープではなく、結果リストか空状態のステータスを待つ。
- ユーザーが `Include archived` を有効にしない限り、アーカイブ済みのノートは除外される。
- CLI の既定は人間が読める形式の出力である。安定したアサーションには `--format json` を使う。
- 結果を開くとブラウザの状態が変わる。別のクエリを証明する前に検索を再度開く。
