# Ruby のマジックリテラル

Ruby の文字列・シンボル・数値・列挙値を整理する場合に読む。

## 既存の定義を再利用する

モデルやドメイン内の定数、採用済みのスキーマや列挙機能を確認する。dry-types の列挙型などで値の集合が定義されているなら、そこを正本にする。実行時検証が不要な定数化のために gem を追加しない。

Rails の ActiveRecord enum が使われている場合は、既存の定義を再利用する。生成される判定メソッドや scope、DB に保存する整数の対応を、独立した定数へ機械的に置き換えない。

## 定義がない場合

既存の列挙機構がなければ、ドメイン内のモジュールやクラスに定数を置く。

```ruby
module UserRole
  ADMIN = 'admin'.freeze
  MEMBER = 'member'.freeze
  GUEST = 'guest'.freeze
end
```

一覧が必要な場合だけ、同じ定数から作る。

```ruby
USER_ROLES = [UserRole::ADMIN, UserRole::MEMBER, UserRole::GUEST].freeze
```

文字列をシンボルへ変換しない。`'admin'` と `:admin` は、比較や外部への出力で同じ契約ではない。コレクションの `freeze` は浅いため、この例では各文字列も凍結している。

呼び出し先が値を書き換える場合は、共有定数への置換で元の挙動が変わらないか確認する。互換性を保てる箇所だけ修正する。

## 分岐と命名

```ruby
def role_label(role)
  case role
  when UserRole::ADMIN then '管理者'
  when UserRole::MEMBER then '一般'
  when UserRole::GUEST then 'ゲスト'
  else
    raise ArgumentError, "Unknown role: #{role.inspect}"
  end
end
```

この例の例外は、不正値を拒否する契約の場合に使う。既存のフォールバックやエラーの挙動は保つ。Ruby の `case` は自動で網羅性を保証しないため、列挙された値と不正値の扱いを関連テストで確認する。

定数は `SCREAMING_SNAKE_CASE` にする。モデル、モジュール、クラスの名前や配置は、既存規約に従う。

```ruby
MAX_RETRY_COUNT = 3
SESSION_TTL_SECONDS = 24 * 60 * 60
```

期間の単位は呼び出し先の契約に合わせる。秒とミリ秒を名前の変更と一緒に変えない。

プロジェクトの RSpec または Minitest、構文チェック、採用済みの RuboCop などで確認する。
