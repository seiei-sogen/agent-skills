# TypeScript のマジックリテラル

TypeScript の文字列・数値・列挙値を整理する場合に読む。

## 採用済みの列挙スキーマを使う

依存関係、ロックファイル、既存コードから、型ライブラリとバージョンを確認する。値の集合をスキーマに1度だけ定義し、型と参照用の値をそこから導出する。

Zod 3・4 の例。

```ts
import { z } from 'zod';

export const UserRoleSchema = z.enum(['admin', 'member', 'guest']);
export type UserRole = z.infer<typeof UserRoleSchema>;

export const USER_ROLES = UserRoleSchema.options;
```

比較や引数では `UserRoleSchema.enum.admin` などを使う。一覧が不要なら `USER_ROLES` は追加しない。

Valibot では `picklist` を使う。既存の列挙オブジェクトを受け取る場合は `enum_` を使い、型は `InferOutput` で導出する。

```ts
import * as v from 'valibot';

export const UserRoleSchema = v.picklist(['admin', 'member', 'guest']);
export type UserRole = v.InferOutput<typeof UserRoleSchema>;
```

## 型ライブラリを使わない場合

採用済みの列挙スキーマが使えない場合は、`as const` オブジェクトを使う。

```ts
export const UserRole = {
  Admin: 'admin',
  Member: 'member',
  Guest: 'guest',
} as const;

export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export const USER_ROLES = Object.values(UserRole);
```

一覧が不要なら `USER_ROLES` は追加しない。`as const` は型の制約であり、実行時にオブジェクトを凍結するものではない。同じ値をスキーマと定数オブジェクトの両方に定義しない。

## 分岐の網羅性を確認する

プロジェクトに網羅性チェックがあれば再利用する。なければ `never` への代入で型チェックできる。次の例は、上の `as const` オブジェクトを使う。

```ts
function label(role: UserRole): string {
  switch (role) {
    case UserRole.Admin: return '管理者';
    case UserRole.Member: return '一般';
    case UserRole.Guest: return 'ゲスト';
    default: {
      const exhaustive: never = role;
      throw new Error(`Unexpected role: ${String(exhaustive)}`);
    }
  }
}
```

既存の分岐にデフォルト値などの挙動がある場合は、それを保つ。網羅性チェックのために例外へ変えない。

## 命名と配置

- 列挙スキーマは `PascalCase` に `Schema` を付ける。
- 定数オブジェクトとそのキーは `PascalCase` にする。
- 単独の数値・文字列定数は `SCREAMING_SNAKE_CASE` にする。一覧は複数形にする。
- 配置はドメイン内の既存構成に合わせる。共通の巨大な定数ファイルを作らない。

```ts
export const MAX_RETRY_COUNT = 3;
export const SESSION_TTL_MS = 24 * 60 * 60 * 1000;
```

## 既存の enum と検証

新規の `enum` は使わず、列挙スキーマか定数オブジェクトを使う。既存の `enum` は、公開 API、数値 enum の逆引き、保存値への影響を確認して置換候補を報告する。Node.js のネイティブ型ストリッピングや `erasableSyntaxOnly` を使う構成では、`enum` の実行時コードも考慮する。

既存の型チェックと関連テストを実行する。ESLint の `no-magic-numbers`、`@typescript-eslint/no-magic-numbers`、`sonarjs/no-duplicate-string` は、導入済みの場合だけ発見の補助として使う。
