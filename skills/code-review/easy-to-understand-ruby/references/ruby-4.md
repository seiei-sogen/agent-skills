# Ruby 4 リファレンス（TypeScript エンジニア向け）

対象コードに出てくる Ruby の書き方を、Ruby にブランクのある TypeScript エンジニアへ正確に説明するための控え。
説明する前に、対象コードに出てくる構文を 2 章と 3 章の表で引き、Ruby 4.0 固有の挙動に触れるときは 1 章で裏を取る。

出典の区別:

- 1 章は [NEWS for Ruby 4.0.0](https://github.com/ruby/ruby/blob/ruby_4_0/NEWS.md)（2025-12-25 リリース）から要点を写したもの。
- 2 章以降は一般に知られた言語仕様の要約。版の記述が心配なときは [docs.ruby-lang.org の NEWS](https://docs.ruby-lang.org/ja/) で確認し、確認できなければ HTML には「要確認」と書く。

## 0. まずバージョンを確かめる

- `.ruby-version`、`Gemfile` の `ruby "..."`、`.tool-versions`、`Dockerfile` の順に探す。見つからなければ `ruby -v`。
- Rails 8.1 は Ruby 3.2 以上で動く。Ruby 4.0 のアプリでも、3.x の書き方はそのまま動く。
- 版が分からないまま「Ruby 4 では」と書かない。

## 1. Ruby 4.0 で変わったこと（NEWS より）

### 1.1 文法

| 変更 | 内容 | TS の人への説明 |
| --- | --- | --- |
| 行頭の論理演算子 | `&&` `\|\|` `and` `or` を行頭に置くと前の行の続きになる（メソッドチェーンの行頭 `.` と同じ扱い） | `if cond1`<br>`   && cond2` が 1 つの条件 |
| `*nil` | 配列展開で `*nil` を渡しても `nil.to_a` を呼ばない（`**nil` が `to_hash` を呼ばないのと同じ） | スプレッドに null を渡せる |

### 1.2 コアクラス

| 変更 | 内容 |
| --- | --- |
| `Set` がコアクラスに | `require "set"` 不要。`Set#inspect` は `Set[1, 2, 3]` 表示。`SortedSet` は削除され、`sorted_set` gem が必要 |
| `Pathname` がコアクラスに | `require "pathname"` 不要 |
| `Array#rfind` 追加 | `array.reverse_each.find` の高速版。`Array#find` も `Enumerable#find` の高速な上書きとして追加 |
| `Kernel#inspect` | `instance_variables_to_inspect` メソッドを定義すると、`inspect` に出す変数を選べる（パスワードを隠すなど） |
| `String#strip` 系 | `strip` `lstrip` `rstrip`（`!` 付きも）が削る文字を引数で指定できる |
| `Enumerator.produce(size:)` | 無限列挙子に大きさを与えられる |
| `Fiber#raise(cause:)` `Thread#raise(cause:)` | `Kernel#raise` と同じく原因例外を付けられる |
| `Math.log1p` `Math.expm1` | 追加 |
| `IO.select` | タイムアウトに `Float::INFINITY` を渡せる |
| `File::Stat#birthtime` | Linux でも statx 対応なら使える |
| `Binding#local_variables` | 番号付きパラメータ（`_1`）を含まなくなった。`Binding#implicit_parameters` 系で `it` と `_1` を扱う |
| `Proc#parameters` | 無名の省略可能引数を `[:opt]` と表示 |
| `Range` | `to_set` が無限 Range を拒む。`overlap?` が無限 Range を正しく扱う |
| ErrorHighlight | `ArgumentError` で呼び出し側と定義側の両方のコードを表示 |

### 1.3 並行処理と実行環境

| 変更 | 内容 |
| --- | --- |
| `Ractor::Port` | Ractor 間通信の新しい仕組み。`port.receive` `port << value` `port.close`。これに伴い `Ractor.yield` と `Ractor#take`、`close_incoming` `close_outgoing` は削除 |
| `Ractor#join` `Ractor#value` | `Thread#join` `Thread#value` 相当。`Ractor.select` は Ractor と Port だけ受け付ける |
| `Ractor.shareable_proc` `Ractor.shareable_lambda` | 共有可能な Proc を作る |
| `Ruby` モジュール | トップレベルに `Ruby` モジュールが正式に定義された |
| `Ruby::Box`（実験的） | 定義（クラス、メソッド、定数）を箱ごとに分離する仕組み |
| ZJIT（実験的） | `--zjit` または `RubyVM::ZJIT.enable` で有効化。4.0.0 時点ではインタプリタより速いが YJIT より遅く、production 利用は非推奨 |
| YJIT | `RubyVM::YJIT.enable(mem_size:, call_threshold:)` が追加 |
| RJIT | `--rjit` は削除 |
| `Class#new` | 全ケースで高速化（特にキーワード引数） |

### 1.4 標準ライブラリ（Gemfile に影響する）

- default gem から bundled gem へ移動: `ostruct` `pstore` `benchmark` `logger` `rdoc` `win32ole` `fiddle` `irb` `reline` `readline`。Bundler 環境ではこれらを `Gemfile` に書かないと `require` できない。Rails アプリでは Rails が依存に含めるものが多いが、`ostruct` と `benchmark` を直接使うコードは要注意。
- `cgi` ライブラリは default gem から削除。残るのは `cgi/escape` の `CGI.escape` `unescape` `escapeHTML` `unescapeHTML` `escapeURIComponent` `unescapeURIComponent` `escapeElement` `unescapeElement` だけ。
- `Net::HTTP` は本文付きリクエストに `Content-Type: application/x-www-form-urlencoded` を自動付与しなくなった。
- RubyGems と Bundler が 4 系。

### 1.5 互換性の変更

- バックトレースに `<internal:...>` フレームが出なくなり、C 実装メソッドも呼び出し元の行として表示される。
- 引数の数が違う `ArgumentError` のメッセージに `Foo#bar` のようにクラス名が付く。
- `ObjectSpace._id2ref` は非推奨。
- `IO` クラスメソッドと `Kernel#open` の先頭 `|` によるプロセス生成は削除。
- `Process::Status#&` `#>>` は削除。
- Unicode 17.0 対応。

## 2. 3.0〜3.4 で入った、ブランクがあると見慣れない書き方

対象コードにこれらが出てきたら、HTML の文法表に必ず載せる。

| 書き方 | 版 | 意味 | TypeScript でいうと |
| --- | --- | --- | --- |
| `{ name:, age: }` / `f(limit:)` | 3.1 | 同名の変数を値にするハッシュ・キーワード引数の省略 | `{ name, age }` |
| `def f(&) = g(&)` | 3.1 | 無名ブロックをそのまま渡す | コールバックをそのまま渡す |
| `def f(*, **) = g(*, **)` | 3.2 | 無名の可変長引数をそのまま渡す | `(...args) => g(...args)` |
| `def square(x) = x * x` | 3.0 | 1 行メソッド（endless method） | `const square = (x) => x * x` |
| `[1, 2].map { it * 2 }` | 3.4 | ブロック引数が 1 つのときの暗黙の名前。`_1` は 2.7 から | `.map((it) => it * 2)` |
| `Point = Data.define(:x, :y)` | 3.2 | 不変の値オブジェクト。`Point.new(x: 1, y: 2)`、`with(x: 3)` で複製 | `Readonly<{x: number; y: number}>` のクラス版 |
| `case value in {status: "ok", body:}` | 3.0 | パターンマッチ。ハッシュや配列を分解して束縛する。`[*, x, *]`（find pattern）は 3.2 で正式 | 分割代入 + `switch` |
| `config => {host:, port:}` | 3.0 | 右代入のパターンマッチ。合わないと `NoMatchingPatternError` | `const {host, port} = config` |
| `value in {status: "ok"}` | 3.0 | パターンに合うかを真偽値で返す | 型ガード |
| `in ^(expr)` | 3.1 | ピン。式の値と一致するかを見る | `case expr:` |
| `**nil` | 3.4 | キーワード引数なしの明示 | `...{}` |
| `Hash#inspect` の表示 | 3.4 | `{name: "x", "k" => 1}` 形式（以前は `{:name=>"x"}`） | コンソール出力の違いだけ |
| エラーメッセージの引用符 | 3.4 | `undefined method 'foo' for an instance of Bar` のようにシングルクォートとクラス名 | スタックトレースの読み方 |
| 文字列リテラルの「chilled」 | 3.4 | `# frozen_string_literal` コメントのないファイルの文字列リテラルを破壊的に変更すると、`-W:deprecated` で警告 | `const` 文字列を変えようとした警告 |
| `Hash.new(capacity: n)` `Array#fetch_values` | 3.4 | 追加 | `new Map()` の初期容量 / 複数キー取得 |
| Prism | 3.4 | 既定のパーサが Prism になった。文法は変わらない | ツールの内部変更 |
| `Set` | 3.2 | `require` なしで使える（autoload）。4.0 でコアクラスに | `Set` |
| `Hash#except` | 3.0 | キーを除いた新しいハッシュ | `Omit` 相当の実行時版 |

## 3. Ruby と TypeScript の対応（版に依らない基本）

説明文ではこの表の「TypeScript でいうと」をそのまま使い、対象コードの行番号を添える。

| Ruby | TypeScript でいうと | 補足 |
| --- | --- | --- |
| `:name`（シンボル） | `'name'` のリテラル型 | 同じ名前のシンボルは同一オブジェクト。ハッシュのキーやメソッド名に使う |
| `nil` | `null` と `undefined` の両方 | `nil` と `false` だけが偽。`0` も `""` も `[]` も真 |
| `foo&.bar` | `foo?.bar` | nil なら nil |
| `x ||= y` | `x ??= y` に近い | ただし `false` のときも代入される |
| `"a #{b}"` | `` `a ${b}` `` | ダブルクォートだけ展開する |
| `<<~SQL ... SQL` | 複数行テンプレート文字列 | `~` は行頭の字下げを取り除く。終端の語は任意 |
| `def foo` 〜 `end` | `foo() {}` | 最後に評価した式が戻り値。`return` は途中で抜けるときだけ |
| `def self.foo` | `static foo()` | クラスメソッド |
| `attr_reader :x` | `get x() { return this.#x }` | `attr_accessor` は setter も |
| `@x` | `this.#x` | インスタンス変数は外から見えない |
| `private`（単独行） | 以降のメソッドが `private` | `private def foo` と 1 行で書くこともある |
| `class A < B` | `class A extends B` | 単一継承 |
| `module M` + `include M` | mixin / interface の実装 | `extend M` はクラスメソッドとして取り込む |
| `A::B` | 名前空間 `A.B` | 先頭の `::A` は最上位から探す（絶対パス） |
| `foo(a, b)` と `foo a, b` | `foo(a, b)` | 呼び出しのかっこは省略できる。クラス本体の `belongs_to :x` は「読み込み時に実行されるメソッド呼び出し」 |
| `foo(key: 1)` | `foo({ key: 1 })` | キーワード引数。`def foo(key:, other: 2)` で必須と既定値 |
| `{ a: 1 }` と `{ "a" => 1 }` | `{ a: 1 }` | キーがシンボルか文字列かは区別される |
| `do \|x\| ... end` / `{ \|x\| ... }` | コールバック `(x) => {}` | ブロック。`yield` で呼ぶ。`&block` で受け取る |
| `-> (x) { x * 2 }` / `lambda` | `(x) => x * 2` | 引数の数を検査する。`proc` は検査しない |
| `method(:foo)` / `&:upcase` | 関数参照 / `(s) => s.toUpperCase()` | |
| `foo?` | `isFoo()` | 真偽値を返す慣習 |
| `foo!` | 例外を投げる版、または破壊的な版 | `save!` は失敗で例外、`save` は `false` |
| `if cond ... elsif ... else ... end` | `if / else if / else` | `unless` は `if (!cond)`。後置 `return x if cond` |
| `case x when 1 then ... end` | `switch` | `when` は `===` で比較。範囲やクラスも書ける |
| `begin ... rescue E => e ... ensure ... end` | `try / catch / finally` | メソッド全体なら `begin` を省略できる |
| `raise ArgumentError, "msg"` | `throw new Error("msg")` | |
| `1..5` / `1...5` | 範囲 | `...` は終端を含まない |
| `arr.map` `select` `reject` `find` `sum` `group_by` `tally` `each_with_object` | `map` `filter` `filter(!)` `find` `reduce` ... | `Enumerable` の共通メソッド |
| `arr.each_slice(2)` `each_cons(2)` `zip` `flat_map` | 手書きのループ | |
| `obj.freeze` | `Object.freeze` | 文字列もオブジェクトなので凍結できる |
| `obj.dup` | 浅いコピー | |
| `Struct.new(:a, :b)` | 値クラス（可変） | `Data.define` は不変版 |
| `respond_to?(:foo)` | `'foo' in obj` | ダックタイピング |
| `send(:foo, 1)` / `public_send` | `obj['foo'](1)` | メソッド名を動的に呼ぶ |
| `define_method` / `method_missing` | Proxy | メタプログラミング。Rails の `find_by_name` などの正体 |
| `puts` / `p` / `pp` | `console.log` | `p` は `inspect` 表示で戻り値も返す。`puts` は `nil` を返す |
| `Integer` / `Float` / `Rational` | `number` | `7 / 2` は `3`（整数除算）。`7.0 / 2` は `3.5` |
| `obj == other` / `equal?` / `eql?` | `===` / 同一性 / ハッシュキー同値 | 配列同士の `==` は要素ごとに比較する |
| `Comparable` + `<=>` | `compareTo` | |
| `ObjectSpace` `GC` | なし | |

## 4. TypeScript の人が踏む落とし穴

HTML の「つまずきやすい点」の候補。対象コードに出ているものだけ採用する。

1. 偽になるのは `nil` と `false` だけ。`if count` は `0` でも真。
2. `and` `or` `not` は `&&` `||` `!` より優先順位が低い。`x = a or b` は `(x = a) or b`。
3. `puts` は `nil` を返すので、メソッドの最後に書くと戻り値が `nil` になる。
4. 文字列は可変。`str << "x"` は元の文字列を変える。`+=` は新しい文字列を作る。
5. シンボルキーと文字列キーは別物。`params[:id]` と `params["id"]` は Rails の `ActionController::Parameters` が同一視しているだけ。
6. ブロックの中の `return` は、ブロックを囲むメソッドから抜ける。`lambda` の `return` はラムダから抜ける。
7. `private` はレシーバを明示した呼び出し（`other.foo`）を禁じるだけで、同じクラスの別インスタンスからも `self.foo` 形式では呼べない。TS の `private` とは境界が違う。
8. クラス本体の直下に書いた式は、ファイル読み込み時に 1 回だけ実行される。`belongs_to` `enum` `scope` `validates` はすべてメソッド呼び出し。
9. `self` はクラス本体ではクラス、メソッド内ではインスタンス。
10. 定数（大文字始まり）は再代入できるが警告が出る。`freeze` しないと中身は変えられる。
11. 多重代入 `a, b = b, a` と配列の自動展開。
12. `Hash#fetch(:key)` はキーがないと例外、`hash[:key]` は `nil`。
13. `Array#first` は `nil` を返すが `Array#fetch(0)` は例外。`first!` はない（Rails の `find` が例外版）。
14. `Integer("12")` は厳密、`"12abc".to_i` は `12`。
15. `require` は Rails アプリではほぼ書かない（Zeitwerk のオートロード）。ファイルパスとクラス名の対応が規約。

## 5. 一次情報

- NEWS for Ruby 4.0.0: https://github.com/ruby/ruby/blob/ruby_4_0/NEWS.md
- Ruby 4.0.0 リリース告知: https://www.ruby-lang.org/en/news/2025/12/25/ruby-4-0-0-released/
- Ruby::Box の説明: https://docs.ruby-lang.org/en/4.0/language/box_md.html
- ZJIT の説明: https://docs.ruby-lang.org/en/master/jit/zjit_md.html
- 日本語リファレンス: https://docs.ruby-lang.org/ja/
