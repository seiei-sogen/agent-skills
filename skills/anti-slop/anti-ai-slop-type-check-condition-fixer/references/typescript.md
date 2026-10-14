# TypeScript の型判定と条件式

TypeScript の型チェック、型ガード、入力・フォーム検証、複合条件を修正する場合に読む。

## 検証機構を選ぶ

依存関係、ロックファイル、既存コードから、採用済みの Zod、Valibot、Yup、Joi、TypeBox、Ajv などと、そのバージョンを確認する。同じ契約のスキーマがあれば再利用する。短い `typeof`、`instanceof`、`Array.isArray` の判定を、形式をそろえるためだけにスキーマへ置き換えない。

スキーマから型を導出できる場合は、実行時検証と型定義を同じ正本へまとめる。たとえば、既存の Zod スキーマなら次のように導出する。

```ts
import { z } from 'zod';

const UserSchema = z.object({ name: z.string() });
type User = z.infer<typeof UserSchema>;
```

Valibot では `v.InferOutput` を使う。型ガードの戻り値が宣言する型と、実際に検証する内容を一致させる。

`parse` の例外と `safeParse` の結果は同じ通知方法ではない。型変換、既定値、未定義・null・空文字列の扱い、余分なプロパティの扱いも含め、元の契約に合う API を使う。

## 条件に名前を付ける

真偽値の変数名は `is` で始める。関数は条件の意味を表す名前にする。

```ts
const isSubmissionAllowed = isSignedIn && isFormValid && hasCapacity;

if (isSubmissionAllowed) {
  submit();
}
```

式を抽出した後も、後続コードで必要な型の絞り込みが維持されていることを型チェックで確かめる。型アサーションで修正漏れを隠さない。

プロジェクトの関連テスト、型チェック、lint を実行する。
