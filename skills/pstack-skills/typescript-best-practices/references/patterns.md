# TypeScript パターン

`SKILL.md` の各規則に対するコード例。基礎となる原則は言語に依存しない。**type-system-discipline** と **boundary-discipline** の原則スキルを参照。

## ブランド型

混同できないようにプリミティブにブランドを付ける。境界で一度だけバリデーションする。下流のコードは型を信頼する。

```ts
type AgentId = string & { readonly __brand: "AgentId" };

function parseAgentId(input: string): AgentId {
  if (!isUUID(input)) throw new Error(`Invalid agent id: ${input}`);
  return input as AgentId;
}

function focusAgent(id: AgentId): void {
  /* input is trusted */
}
```

`readonly __brand: 'X'` の形に合わせる。新しい規約を発明しない。

## 判別可能ユニオン

バリアントをリテラルの判別子でモデル化する。すべてのバリアントがフィールド名を共有し、各バリアントの値が一意なので、不可能な組み合わせを表現できない。

```ts
// Don't. Boolean + optionals lets contradictory states exist.
type DiffState = { loading: boolean; diff?: GitDiff; error?: string };

// Do. Only valid states exist.
type DiffState =
  | { kind: "loading" }
  | { kind: "ready"; diff: GitDiff }
  | { kind: "error"; error: string };
```

判別子の名前を 1 つ選び（`kind`、`type`、`tag`）、それを守る。

## 構成的モデリング

緩い型を実行時チェックで制限するのではなく、すべてが正当な部品から型を組み立てる。

非空は、可変長タプルで表す。

```ts
type NonEmpty<T> = [T, ...T[]];

// Don't: T[] plus a length check every caller must repeat
function pickWinner(entries: string[]): string {
  if (entries.length === 0) throw new Error("no entries");
  return entries[Math.floor(Math.random() * entries.length)];
}

// Do: an empty value of the type can't exist
function pickWinner(entries: NonEmpty<string>): string {
  return entries[Math.floor(Math.random() * entries.length)];
}
```

素の `T[]` が届く場所では、ガードで一度だけ絞り込む。その事実は以後、型の中を伝わる。

```ts
const isNonEmpty = <T>(arr: T[]): arr is NonEmpty<T> => arr.length > 0;
```

偶数長は、ペアとして表す。

```ts
type Pairs<T> = [T, T][];
```

時間範囲は、開始と継続時間として表す。

```ts
// Don't: a comment holds the invariant
type TimeRange = { start: Date; end: Date }; // start <= end

// Do: a negative range can't be written; derive end when needed
type TimeRange = { start: Date; durationMs: number };
```

`durationMs` は素の number のままにする。ブランドを付けるのは（ブランド型の節に従って）、継続時間が期待される場所に生の数値が渡されうる場合だけであり、反射的に付けない。不正な状態を構築不可能にする表現を選び、そのうえで必要な読み取り方を公開する（`pairs.flat()`、`rangeEnd()` ヘルパー）。

## 最もシンプルな全域型

すべてを強めない。それに対するすべての操作が全域であるなら `T[]` のままにする。

```ts
const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0); // [] is 0, fine
```

緩い型が使用箇所で嘘を強いるときに強める。その兆候は `!`、`arr[0] as T`、そして「起こりえないはず」の throw である。

```ts
// Don't: partiality smuggled past the compiler
function newestSession(sessions: Session[]): Session {
  return sessions.at(0)!;
}

// Do: strengthen the input; the assertion disappears
function newestSession(sessions: NonEmpty<Session>): Session {
  return sessions[0];
}
```

結果を `Session | undefined` に弱めるのが、もう一方の全域なシグネチャである。

## `any` より `unknown`

外部データは常に `unknown` である。使う前に絞り込む。

```ts
// Don't
function handle(input: any) {
  return input.foo.bar;
}

// Do
function handle(input: unknown) {
  if (typeof input === "object" && input !== null && "foo" in input) {
    // narrowed; compiler verifies access
  }
}
```

外部ソースには、RPC ペイロード、`JSON.parse`、`postMessage`、IPC、ファイル内容、環境変数、データベースの結果が含まれる。

## 手書きガードより先にスキーマ

外部データに対してプロパティごとの型ガードを書く前に、リポジトリの実行時スキーマライブラリと既存のスキーマを探す。1 つのスキーマにバリデーションを所有させ、そこから TypeScript の型を導出する。互いにずれていきうるスキーマ、重複した interface、ガードの 3 つを維持しない。

```ts
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  role: z.enum(["admin", "member"]),
});

type User = z.infer<typeof UserSchema>;

function parseUser(input: unknown): User {
  return UserSchema.parse(input);
}
```

失敗が想定された分岐であるなら `safeParse` を使う。リポジトリが別のスキーマライブラリを使っているなら、それに相当する推論ヘルパーを使う。ガード 1 つのために新しいスキーマ依存を追加しない。この規則は、コードベースがすでに信頼しているスキーマシステムを優先する。

## `as` キャスト禁止

すべての `as` は潜在的な実行時クラッシュである。型システムが主張を検証した後にだけキャストする。

```ts
// Don't
const user = data as User;

// Do. Earn the cast at the boundary.
function parseUser(data: unknown): User {
  if (typeof data !== "object" || data === null) {
    throw new Error("expected object");
  }
  if (!("id" in data) || typeof (data as Record<string, unknown>).id !== "string") {
    throw new Error("expected id");
  }
  // ... validate all fields
  return data as User; // OK, earned cast after full validation
}
```

既存コードから `as` を取り除くリファクタリングをするときは、TypeScript が推論できない理由を特定する。

- 判別子の欠如: 判別子を追加し、判別可能ユニオンに切り替える。
- 過度に広いソース型（例: `Record<string, unknown>`）: 絞り込む。
- 型付けされていない境界: パース関数またはスキーマを追加する。
- 本当に表現不可能: ブランド型または `satisfies` を使う。

## 絞り込みの階層

最良から最後の手段まで順に。

1. **判別可能ユニオンの switch / if。** コンパイラが自動的に絞り込む。
2. **`in` 演算子。** `"key" in obj` は、そのキーを含むバリアントに絞り込む。
3. **`typeof` / `instanceof`。** プリミティブとクラスインスタンス向け。
4. **ユーザー定義型ガード。** 上記で足りないとき。
5. **`as` キャスト。** バリデーションの後にだけ。

```ts
function area(s: Shape): number {
  if ("radius" in s) return Math.PI * s.radius ** 2; // narrowed to circle
  return s.width * s.height; // narrowed to rect
}
```

## 型ガード

ガードは主張を実際に検証しなければならない。嘘をつくガードは `as` より悪い。

```ts
function isCircle(s: Shape): s is Shape & { kind: "circle" } {
  return s.kind === "circle";
}
```

可能なときは判別子による絞り込みを優先する。

## 網羅性

default 節で、判別子を `never` 型のローカル変数に代入する。

```ts
// Value-returning switch
function area(s: Shape): number {
  switch (s.kind) {
    case "circle":
      return Math.PI * s.radius ** 2;
    case "rect":
      return s.width * s.height;
    default: {
      const _exhaustive: never = s;
      return _exhaustive;
    }
  }
}

// Void switch
function handle(s: Shape): void {
  switch (s.kind) {
    case "circle":
      drawCircle(s);
      break;
    case "rect":
      drawRect(s);
      break;
    default: {
      const _exhaustive: never = s;
      void _exhaustive;
    }
  }
}
```

値を返す switch では return 形式、文としての switch では void 形式。

## `as` より `satisfies`

`satisfies` はリテラル型を広げずにバリデーションする。

```ts
// Don't. Widens, loses literal types.
const config = { theme: "dark", cols: 3 } as Config;

// Do. Validates AND preserves literal types.
const config = { theme: "dark", cols: 3 } satisfies Config;
// config.theme is "dark" (literal), not string
```

## 境界バリデーション

データが入ってくる場所で一度だけバリデーションする。内部では型を信頼する。**boundary-discipline** 原則スキルを参照。

- **ワイヤフォーマット**（proto、JSON-RPC）: 前方互換な変更が古いクライアントを壊さないように、`ignoreUnknownFields` でパースする。
- **永続化された JSON:** パースを try/catch で囲んだ、バージョン付きの blob。
- 呼び出し連鎖の深いところで**再バリデーションしない**。

## スキーマ由来の型

`.proto`、OpenAPI 仕様、GraphQL スキーマ、またはデータベースマイグレーションがすでに形を定義しているなら、それを重複させるのではなく生成された型から導出する。

```ts
// Don't. Duplicate shape, drifts when the schema changes.
type CheckSummary = {
  totalCount: number;
  checks: { name: string; status: string }[];
};
function renderChecks(s: CheckSummary) {
  /* ... */
}

// Do. Derive from the generated schema type.
import type { ChecksMessage } from "<generated module>";
function renderChecks(s: Pick<ChecksMessage, "totalCount" | "checks">) {
  /* ... */
}
```

新しい interface を書く前に `Pick`、`Omit`、`Parameters`、`ReturnType`、`Awaited`、`typeof` をまず使う。

## オブジェクト引数

```ts
// Don't. Swap two args, still compiles.
openFile(uri, {
  startLineNumber: 10,
  startColumn: 1,
  endLineNumber: 10,
  endColumn: 1,
});

// Do. Order-independent, self-documenting.
openFile({
  uri,
  selection: {
    startLineNumber: 10,
    startColumn: 1,
    endLineNumber: 10,
    endColumn: 1,
  },
});
```

ホットパスでは省く。フレームごとのレンダリング、トークナイザ、パーサ、アロケーションコストが問題になるタイトループ内のあらゆるもの。
