# 良いテストと悪いテスト

## 良いテスト

**統合スタイル**: 内部部分のモックではなく、実際のインターフェースを通してテストする。

```typescript
// GOOD: Tests observable behavior
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

特徴:

- ユーザーや呼び出し元が関心を持つ挙動をテストする
- 公開APIのみを使用する
- 内部リファクタに耐える
- HOWではなくWHATを記述する
- テストごとに一つの論理的なアサーション

## 悪いテスト

**実装の詳細に依存するテスト**: 内部構造に結びついている。

```typescript
// BAD: Tests implementation details
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

警告サイン:

- 内部の共同作業者をモックする
- プライベートメソッドをテストする
- 呼び出し回数／順序の検証
- 振る舞いを変えずにリファクタリングするとテストが壊れる
- テスト名が何をするかではなく、どのようにするかを説明している
- インターフェイスではなく外部手段で検証する

```typescript
// BAD: Bypasses interface to verify
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD: Verifies through interface
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

**同語反復的なテスト**：期待値が実装を再述しているため、テストは作成上自動的にパスする。

```typescript
// BAD: Expected value is recomputed the way the code computes it
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD: Expected value is an independent, known literal
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```
