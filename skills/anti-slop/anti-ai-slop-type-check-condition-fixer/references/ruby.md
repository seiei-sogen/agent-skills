# Ruby の型判定と条件式

Ruby の型判定、入力・フォーム検証、`if`・`unless` などの複合条件を修正する場合に読む。

## 検証機構を選ぶ

Gemfile、ロックファイル、既存コードから、採用済みの検証機構を確認する。dry-schema、dry-validation、Rails の ActiveModel validations などが同じ契約を表している場合は再利用する。

検証機構は用途に合わせる。入力用スキーマでモデルの保存時検証を置き換えたり、単純な `is_a?` の判定のために gem を追加したりしない。

既存コードがオブジェクトの能力を調べているなら、`respond_to?` を特定のクラスへの所属判定へ機械的に置き換えない。動的な契約まで静的な型定義で表そうとせず、実際に必要な実行時検証を保つ。

キーの文字列・シンボルの違い、型変換、既定値、nil・空文字列の扱い、モデルの errors や例外による通知を確認する。スキーマ化によって受理する入力や検証のタイミングを変えない。

## 条件に名前を付ける

判定メソッドには `submission_allowed?` のような名前を使う。ローカル変数は `is_submission_allowed` など、条件の意味が分かる名前を既存規約に合わせて付ける。

```ruby
is_submission_allowed = signed_in? && form_valid? && has_capacity?

if is_submission_allowed
  submit
end
```

Ruby では false と nil だけが偽で、0 や空文字列は真になる。`&&` と `||` は真偽値以外を返すこともあるため、抽出時に `!!` などで値を変換しない。`and` と `or` は代入との優先順位が異なるため、演算子もそのまま保つ。

`unless` の否定の向きや、短絡評価で呼び出されないメソッドを保つ。Rails の `present?` や `blank?` は、元の真偽判定と同じ受理条件になる場合だけ使う。

プロジェクトの RSpec または Minitest、構文チェック、採用済みの RuboCop などで確認する。
