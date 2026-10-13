---
name: anti-ai-slop-no-magic-literal
description: TypeScript コードのレビューと修正。条件分岐・比較・引数に直接書かれた文字列リテラル（マジックリテラル）や数値リテラルを検出し、`as const` オブジェクト + 導出型のパターンに置き換える。AI が生成したコードのレビュー時、既存コードのリファクタ時、`if (x === 'active')` のような比較を見かけたときに使う。
---

# マジックリテラル撲滅レビュー

## 目的

「意味を持つ文字列/数値が、コードの中に裸のリテラルとして散らばっている」状態を潰す。
LLM が生成したコードで頻出する。型は通るが、タイポがコンパイルエラーにならず、値の一覧がどこにも存在しない。

## スコープ外（過剰適用しない）

これも同じくらい重要。定数化は手段であって目的ではない。

- 一箇所でしか出てこず、意味が自明なもの（`path.join(dir, 'index.html')` の `'index.html'`）
- ログメッセージ、エラーメッセージの本文
- テストコード内の固定値（むしろベタ書きのほうが読める）
- 外部仕様で固定された 1 回きりのキー（`headers['content-type']`）
- 定数が 1 個しかない「列挙」

迷ったら基準はこれ: **「この値の取りうる全体集合を、読み手が知る必要があるか」**。必要ならパターン適用。不要なら放置。

---

## 検出パターン

以下を grep 的に洗い出す。

| # | 症状 | 例 |
|---|---|---|
| 1 | 等値比較の右辺がリテラル | `if (user.role === 'admin')` |
| 2 | `switch` の `case` がリテラル | `case 'pending':` |
| 3 | 配列リテラルへの所属判定 | `['a','b'].includes(x)` |
| 4 | 引数にリテラルを渡す | `setStatus('done')` |
| 5 | オブジェクトのキーにリテラル | `config['production']` |
| 6 | 同じ文字列が 2 箇所以上に出現 | `'UTF-8'` があちこち |
| 7 | 裸の `enum` 宣言 | `enum Role { ... }` |
| 8 | マジックナンバー | `if (retry > 3)` / `setTimeout(f, 86400000)` |

7 の `enum` は erasableSyntaxOnly / Node のネイティブ型ストリッピングと相性が悪く、実行時に値を持つため tree-shaking も効きにくい。新規で書かない。既存があれば置き換え候補として報告する（破壊的変更になるので、修正するかは人間に確認）。

---

## 修正パターン

### 基本形: 型ライブラリの列挙スキーマ

```ts
// Zod 3 / 4
export const UserRoleSchema = z.enum(['admin', 'member', 'guest']);
export type UserRole = z.infer<typeof UserRoleSchema>;

UserRoleSchema.enum.admin; // 'admin'
```

プロジェクトで使っている型ライブラリの列挙機能を基本形にする。値の集合はスキーマに一度だけ定義し、型はそこから導出する。Valibot なら `v.picklist` を使う（既存の enum を受け取る場合は `v.enum_`）。

```ts
export const UserRoleSchema = v.picklist(['admin', 'member', 'guest']);
export type UserRole = v.InferOutput<typeof UserRoleSchema>;
```

型ライブラリが使えない場合だけ、`as const` オブジェクトを使う。

```ts
export const UserRole = {
  Admin: 'admin',
  Member: 'member',
  Guest: 'guest',
} as const;

export type UserRole = (typeof UserRole)[keyof typeof UserRole];
```

### 一覧が必要なとき

Zod ではスキーマから取得する。

```ts
export const USER_ROLES = UserRoleSchema.options;
```

型ライブラリが使えない場合は、フォールバックのオブジェクトから導出する。

```ts
export const USER_ROLES = Object.values(UserRole);
```

### `switch` の網羅性チェックを添える

置き換えたら、分岐が網羅されていることを型で保証する。

```ts
function label(role: UserRole): string {
  switch (role) {
    case UserRoleSchema.enum.admin:  return '管理者';
    case UserRoleSchema.enum.member: return '一般';
    case UserRoleSchema.enum.guest:  return 'ゲスト';
    default: return assertNever(role);
  }
}

function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${String(x)}`);
}
```

これがあると、定数を追加したときに修正漏れがコンパイルエラーになる。マジックリテラル撲滅の実利はここに出る。

同じ値をスキーマとオブジェクトに二重定義しない。まず `package.json` と既存コードを確認し、導入済みの型ライブラリとそのバージョンに合う API を使う。

### マジックナンバー

同様に名前を与える。単位を名前に含めること。

```ts
export const MAX_RETRY_COUNT = 3;
export const SESSION_TTL_MS = 24 * 60 * 60 * 1000;
```

---

## 命名規約

- 列挙スキーマ: `PascalCase` + `Schema`（`UserRoleSchema`）
- 型ライブラリが使えない場合の定数オブジェクト: `PascalCase`（型名と揃える）、キーも `PascalCase`
- 単独のスカラ定数: `SCREAMING_SNAKE_CASE`
- 配列の一覧: 複数形の `SCREAMING_SNAKE_CASE`（`USER_ROLES`）
- 値の文字列そのものは、外部仕様（DB の値、API の値）に合わせる。内部都合で勝手に変えない

## 配置

- そのドメインのモジュール内に置く（`features/user/constants.ts` など）
- プロジェクト直下の巨大な `constants.ts` に全部集めない。関係ないものが相互に依存し始める
- 1 箇所でしか使わないなら、使う側のファイルの先頭に置くだけでよい

---

## 作業手順

1. **検出**: 対象ファイル（または差分）を読み、上の検出パターン 1〜8 に当たる箇所を列挙する。
2. **選別**: スコープ外の基準に照らして落とす。残ったものだけを対象にする。
3. **既存定数の確認**: 同じ値の定数がすでに定義されていないか検索する（重複定義を増やすのは最悪）。
4. **修正**: 型ライブラリの列挙スキーマを追加し、型と全参照箇所をそこから導出する。型ライブラリが使えない場合だけオブジェクトを使う。`switch` があれば `assertNever` を添える。
5. **検証**: 型チェック（`tsc --noEmit` 相当）とテストを実行する。実行できない環境なら、実行していないことを明記する。
6. **報告**: 下記フォーマットで出す。

## 報告フォーマット

```
## 修正した箇所
- src/features/user/guard.ts:14  'admin' → UserRoleSchema.enum.admin （他 3 箇所で同値を使用）
- src/api/order.ts:52  switch の 4 case を OrderStatusSchema に統一、assertNever 追加

## 見送った箇所（理由つき）
- src/lib/path.ts:8  'index.html' — 単一箇所・自明のため

## 判断を仰ぎたい箇所
- src/types/role.ts:1  enum Role が公開 API として export されている。
  列挙スキーマへの置き換えは破壊的変更になる可能性があるため未着手。
```

修正していないものを「修正した」と書かない。確認していないものを「確認した」と書かない。

---

## 補助（任意）

機械的に拾いたい場合、ESLint の以下が近い仕事をする。ただし誤検知が多く、スコープ外の基準を機械は判定できないので、CI で強制するより手元の発見補助として使う。

- `no-magic-numbers` / `@typescript-eslint/no-magic-numbers`
- `sonarjs/no-duplicate-string`（`eslint-plugin-sonarjs`）
