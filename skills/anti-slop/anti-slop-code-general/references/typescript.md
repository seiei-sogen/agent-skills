# TypeScript・JavaScript の AI Slop

TypeScript または JavaScript の変更に適用する。型構文は TypeScript ファイルに限る。JavaScript で型検査を使う場合は、採用済みの JSDoc などの規約で契約を表し、TypeScript の構文を直接書かない。

## TypeScript の広い型と型アサーションを見直す

| 兆候 | 優先する実装 | 元の実装を残す条件 |
| --- | --- | --- |
| 内部の `unknown`、`any`、`Record<string, unknown>` | 境界で確定した具体的なドメイン型 | その関数自体が解析境界である |
| `typeof`、`in`、`instanceof` の繰り返し | 境界での解析、または入力元の型修正 | 入力が実際に複数の型を取り得る |
| 最後に `as T` を使うガード | 実際の検証、または外部契約に裏付けられた局所的な型アサーション | 文書化された保証を最も狭く明確に表せるのが型アサーションである |
| 既知の構造を扱う `asX`、`isX`、`safeX`、`extractX`、`normalizeX` | 型付けされた値への直接アクセス | 再利用されるドメイン上の不変条件を表す |
| `Partial<LargeType>` | 受け入れるフィールドだけの小さな型 | すべてのフィールドの部分更新を受け入れる |
| null と undefined を同時に許す型 | 契約に必要な欠損状態 | 各状態に異なる観測可能な意味がある |
| 防御目的のオプショナルフィールド | ドメイン上必須なら必須フィールド | 欠損がサポートされる状態である |
| キーが既知の `Record<string, Handler>` | `Record<EventName, Handler>` または型付きオブジェクト | キーが本当に任意である |
| `event: string` と `data: unknown` のペイロード | 判別可能なユニオン | イベントが型システム外から動的に登録される |

採用済みのスキーマから型を導出する。手書きの判定を変更する場合は、[TypeScript の型判定と条件式](../../anti-ai-slop-type-check-condition-fixer/references/typescript.md) の API 選択と型の絞り込みの基準を使う。

## 変換と空フォールバックを検証と混同しない

`String(value)`、`Number(value)`、`Boolean(value)`、テンプレート文字列、`!!value` は入力検証ではない。`value ?? ""`、`value ?? {}`、`value ?? []`、早期の `return undefined` は、欠損が契約の一部である場合だけ使う。

MongoDB・Mongoose などの永続化型はスキーマに合わせる。`ObjectId` が保証される値は、その型で必要な操作を直接呼ぶ。混在する形式、移行中のデータ、欠損可能なデータ、外部投入データのチェックは残す。

## 標準機能のラッパーを減らす

`JSON.parse`、`Array.isArray`、`Object.keys`、`Object.entries`、`trim`、`toLowerCase`、`Map`、`Set` は直接使う。ラッパーを残す場合はドメイン上の意味が必要である。

再利用が仮定にすぎない `safeCast<T>`、`getValue<T>`、`normalize<T>`、`ensure<T>` などは、具体的な処理へ置き換える。型や入力契約を修正した後は、不要になったヘルパーと型を削除する。

## 非同期処理とコールバックの契約を保つ

既存の Promise を返すだけの `new Promise` や `async` 関数は削除候補にする。`async` を外すと同期例外の通知方法や戻り値の同一性が変わる場合があるため、単純な委譲に見えても契約を確認する。

`return await` の削除では、周囲の例外捕捉や後始末のタイミングを保つ。コールバックを直接の関数参照に置き換える場合は、`this`、引数、評価のタイミングを保つ。

型検査を使う構成では型チェックを行い、すべての構成で関連テストと採用済みの lint を実行する。
